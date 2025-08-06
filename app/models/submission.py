from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId

class AssignmentBase(BaseModel):
    user_id: PyObjectId
    pdf_id: PyObjectId

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentResponse(AssignmentBase):
    id: Optional[Union[str, PyObjectId]] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    is_quiz_completed: bool = False
    quiz_completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class AssignmentInDB(AssignmentBase):
    id: Optional[Union[str, PyObjectId]] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    is_quiz_completed: bool = False
    quiz_completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class QuizSubmissionBase(BaseModel):
    user_id: PyObjectId
    quiz_id: PyObjectId

class QuizSubmissionCreate(QuizSubmissionBase):
    responses_json: Optional[Dict[str, Any]] = None
    in_progress_json: Optional[Dict[str, Any]] = None

class QuizSubmissionResponse(QuizSubmissionBase):
    id: Optional[Union[str, PyObjectId]] = None
    responses_json: Optional[Dict[str, Any]] = None
    in_progress_json: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    submitted_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class QuizSubmissionInDB(QuizSubmissionBase):
    id: Optional[Union[str, PyObjectId]] = None
    responses_json: Optional[Dict[str, Any]] = None
    in_progress_json: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    submitted_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True 