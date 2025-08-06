from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from ..utils.auth import get_current_user_from_token
from ..utils.file_upload import save_upload_file, extract_text_from_pdf
from ..services.llm_quiz_gen import LLMQuizGenerator
from ..core.db import get_database
from ..models.pdf import PDFAssignmentRequest
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/admin", tags=["Admin"])
security = HTTPBearer()

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current admin user"""
    payload = get_current_user_from_token(credentials.credentials)
    if payload["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return payload

@router.post("/upload_pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    current_admin: dict = Depends(get_current_admin)
):
    """Upload PDF and auto-generate quiz"""
    db = get_database()
    
    # Save PDF file
    file_path = await save_upload_file(file)
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(file_path)
    
    # Generate quiz using LLM
    quiz_generator = LLMQuizGenerator()
    quiz_questions = await quiz_generator.generate_quiz_from_text(pdf_text)
    
    # Debug: Print quiz questions JSON to terminal
    print("Generated Quiz Questions:", quiz_questions)

    # Save quiz questions JSON to a file
    with open("quiz_questions.json", "w") as file:
        import json
        json.dump(quiz_questions, file, indent=4)

    # Save PDF document
    pdf_doc = {
        "title": title,
        "description": description,
        "file_url": file_path,
        "uploaded_by": ObjectId(current_admin["sub"]),
        "created_at": datetime.utcnow()
    }
    
    pdf_result = await db.pdf_documents.insert_one(pdf_doc)
    pdf_id = pdf_result.inserted_id
    
    # Save quiz
    quiz_doc = {
        "pdf_id": pdf_id,
        "questions_json": quiz_questions,
        "created_at": datetime.utcnow()
    }
    
    quiz_result = await db.quizzes.insert_one(quiz_doc)
    
    return {
        "message": "PDF uploaded and quiz generated successfully",
        "pdf_id": str(pdf_id),
        "quiz_id": str(quiz_result.inserted_id),
        "questions_count": len(quiz_questions)
    }

@router.post("/assign_pdf")
async def assign_pdf(
    assignment_data: PDFAssignmentRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """Assign PDF to employees"""
    db = get_database()
    
    # Validate PDF exists
    pdf = await db.pdf_documents.find_one({"_id": ObjectId(assignment_data.pdf_id)})
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Create assignments
    assignments = []
    for user_id in assignment_data.user_ids:
        # Check if assignment already exists
        existing = await db.assignments.find_one({
            "user_id": ObjectId(user_id),
            "pdf_id": ObjectId(assignment_data.pdf_id)
        })
        
        if not existing:
            assignment = {
                "user_id": ObjectId(user_id),
                "pdf_id": ObjectId(assignment_data.pdf_id),
                "is_read": False,
                "is_quiz_completed": False,
                "created_at": datetime.utcnow()
            }
            assignments.append(assignment)
    
    if assignments:
        await db.assignments.insert_many(assignments)
    
    return {
        "message": f"PDF assigned to {len(assignments)} users",
        "assigned_count": len(assignments)
    }

@router.get("/users")
async def get_all_users(current_admin: dict = Depends(get_current_admin)):
    """Get all employees"""
    db = get_database()
    
    users = await db.users.find({"role": "employee"}).to_list(length=100)
    
    return [
        {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "created_at": user["created_at"]
        }
        for user in users
    ]

@router.get("/user/{user_id}")
async def get_user_progress(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get user's progress and scores"""
    db = get_database()
    
    # Get user
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's assignments
    assignments = await db.assignments.find({"user_id": ObjectId(user_id)}).to_list(length=100)
    
    # Get detailed assignment info
    detailed_assignments = []
    for assignment in assignments:
        pdf = await db.pdf_documents.find_one({"_id": assignment["pdf_id"]})
        if pdf:
            detailed_assignments.append({
                "pdf_title": pdf["title"],
                "is_read": assignment["is_read"],
                "read_at": assignment.get("read_at"),
                "is_quiz_completed": assignment["is_quiz_completed"],
                "quiz_completed_at": assignment.get("quiz_completed_at")
            })
    
    return {
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        },
        "assignments": detailed_assignments
    }

@router.get("/pdf_status/{pdf_id}")
async def get_pdf_status(
    pdf_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get progress status for a specific PDF"""
    db = get_database()
    
    # Get PDF
    pdf = await db.pdf_documents.find_one({"_id": ObjectId(pdf_id)})
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Get all assignments for this PDF
    assignments = await db.assignments.find({"pdf_id": ObjectId(pdf_id)}).to_list(length=100)
    
    # Get user details for each assignment
    detailed_assignments = []
    for assignment in assignments:
        user = await db.users.find_one({"_id": assignment["user_id"]})
        if user:
            detailed_assignments.append({
                "user_name": user["name"],
                "user_email": user["email"],
                "is_read": assignment["is_read"],
                "read_at": assignment.get("read_at"),
                "is_quiz_completed": assignment["is_quiz_completed"],
                "quiz_completed_at": assignment.get("quiz_completed_at")
            })
    
    return {
        "pdf_title": pdf["title"],
        "total_assignments": len(detailed_assignments),
        "read_count": sum(1 for a in detailed_assignments if a["is_read"]),
        "completed_count": sum(1 for a in detailed_assignments if a["is_quiz_completed"]),
        "assignments": detailed_assignments
    }