from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from ..utils.auth import get_current_user_from_token
from ..core.db import get_database
from ..models.quiz import QuizSubmissionRequest
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/employee", tags=["Employee"])
security = HTTPBearer()

async def get_current_employee(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current employee user"""
    payload = get_current_user_from_token(credentials.credentials)
    if payload["role"] not in ["employee", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required"
        )
    return payload

@router.get("/my_pdfs")
async def get_my_pdfs(current_employee: dict = Depends(get_current_employee)):
    """Get PDFs assigned to current employee"""
    db = get_database()
    
    # Get assignments for current user
    assignments = await db.assignments.find({"user_id": ObjectId(current_employee["sub"])}).to_list(length=100)
    
    # Get detailed PDF info
    pdfs = []
    for assignment in assignments:
        pdf = await db.pdf_documents.find_one({"_id": assignment["pdf_id"]})
        if pdf:
            # Get quiz submission if exists
            quiz = await db.quizzes.find_one({"pdf_id": assignment["pdf_id"]})
            submission = None
            if quiz:
                submission = await db.quiz_submissions.find_one({
                    "user_id": ObjectId(current_employee["sub"]),
                    "quiz_id": quiz["_id"]
                })
            
            pdfs.append({
                "pdf_id": str(pdf["_id"]),
                "title": pdf["title"],
                "description": pdf.get("description", ""),
                "file_url": pdf["file_url"],
                "is_read": assignment["is_read"],
                "read_at": assignment.get("read_at"),
                "is_quiz_completed": assignment["is_quiz_completed"],
                "quiz_completed_at": assignment.get("quiz_completed_at"),
                "score": submission["score"] if submission else None
            })
    
    return pdfs

@router.post("/mark_read/{pdf_id}")
async def mark_pdf_as_read(
    pdf_id: str,
    current_employee: dict = Depends(get_current_employee)
):
    """Mark a PDF as read"""
    db = get_database()
    
    # Update assignment
    result = await db.assignments.update_one(
        {
            "user_id": ObjectId(current_employee["sub"]),
            "pdf_id": ObjectId(pdf_id)
        },
        {
            "$set": {
                "is_read": True,
                "read_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF assignment not found"
        )
    
    return {"message": "PDF marked as read"}

@router.get("/quiz/{pdf_id}")
async def get_quiz(
    pdf_id: str,
    current_employee: dict = Depends(get_current_employee)
):
    """Get quiz for a PDF with saved progress"""
    db = get_database()
    
    # Get quiz
    quiz = await db.quizzes.find_one({"pdf_id": ObjectId(pdf_id)})
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found for this PDF"
        )
    
    # Get saved progress
    submission = await db.quiz_submissions.find_one({
        "user_id": ObjectId(current_employee["sub"]),
        "quiz_id": quiz["_id"]
    })
    
    return {
        "quiz_id": str(quiz["_id"]),
        "questions": quiz["questions_json"],
        "saved_answers": submission["in_progress_json"] if submission else None,
        "is_completed": submission["score"] is not None if submission else False
    }

@router.post("/save_quiz_progress")
async def save_quiz_progress(
    quiz_id: str,
    answers: Dict[str, Any],
    current_employee: dict = Depends(get_current_employee)
):
    """Save incomplete quiz answers"""
    db = get_database()
    
    # Upsert submission with in-progress answers
    await db.quiz_submissions.update_one(
        {
            "user_id": ObjectId(current_employee["sub"]),
            "quiz_id": ObjectId(quiz_id)
        },
        {
            "$set": {
                "in_progress_json": answers,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return {"message": "Quiz progress saved"}

@router.post("/submit_quiz")
async def submit_quiz(
    submission_data: QuizSubmissionRequest,
    current_employee: dict = Depends(get_current_employee)
):
    """Submit quiz and calculate score"""
    db = get_database()
    
    # Get quiz
    quiz = await db.quizzes.find_one({"_id": ObjectId(submission_data.quiz_id)})
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Calculate score
    questions = quiz["questions_json"]
    correct_answers = 0
    total_questions = len(questions)
    
    for i, question in enumerate(questions):
        user_answer = submission_data.answers.get(str(i))
        if user_answer == question["answer"]:
            correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Save submission
    submission_doc = {
        "user_id": ObjectId(current_employee["sub"]),
        "quiz_id": ObjectId(submission_data.quiz_id),
        "responses_json": submission_data.answers,
        "in_progress_json": None,  # Clear in-progress
        "score": score,
        "submitted_at": datetime.utcnow()
    }
    
    await db.quiz_submissions.update_one(
        {
            "user_id": ObjectId(current_employee["sub"]),
            "quiz_id": ObjectId(submission_data.quiz_id)
        },
        {"$set": submission_doc},
        upsert=True
    )
    
    # Update assignment
    pdf_id = quiz["pdf_id"]
    await db.assignments.update_one(
        {
            "user_id": ObjectId(current_employee["sub"]),
            "pdf_id": pdf_id
        },
        {
            "$set": {
                "is_quiz_completed": True,
                "quiz_completed_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "message": "Quiz submitted successfully",
        "score": score,
        "correct_answers": correct_answers,
        "total_questions": total_questions
    }

@router.get("/my_scores")
async def get_my_scores(current_employee: dict = Depends(get_current_employee)):
    """Get employee's quiz scores"""
    db = get_database()
    
    # Get all submissions for current user
    submissions = await db.quiz_submissions.find({
        "user_id": ObjectId(current_employee["sub"]),
        "score": {"$ne": None}  # Only completed quizzes
    }).to_list(length=100)
    
    # Get detailed score info
    scores = []
    for submission in submissions:
        quiz = await db.quizzes.find_one({"_id": submission["quiz_id"]})
        if quiz:
            pdf = await db.pdf_documents.find_one({"_id": quiz["pdf_id"]})
            if pdf:
                scores.append({
                    "pdf_title": pdf["title"],
                    "score": submission["score"],
                    "submitted_at": submission["submitted_at"],
                    "total_questions": len(quiz["questions_json"])
                })
    
    return scores 