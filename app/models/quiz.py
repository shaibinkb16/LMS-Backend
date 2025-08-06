from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId

class QuestionBase(BaseModel):
    question: str
    options: List[str]
    answer: str

class QuizBase(BaseModel):
    pdf_id: PyObjectId

class QuizCreate(QuizBase):
    questions_json: List[QuestionBase]

class QuizResponse(QuizBase):
    id: Optional[Union[str, PyObjectId]] = None
    questions_json: List[QuestionBase]
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class QuizInDB(QuizBase):
    id: Optional[Union[str, PyObjectId]] = None
    questions_json: List[QuestionBase]
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class QuizSubmissionRequest(BaseModel):
    quiz_id: str
    answers: Dict[str, Any] 