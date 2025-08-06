from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId

class PDFDocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class PDFDocumentCreate(PDFDocumentBase):
    pass

class PDFDocumentResponse(PDFDocumentBase):
    id: Optional[Union[str, PyObjectId]] = None
    file_url: str
    uploaded_by: PyObjectId
    created_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class PDFDocumentInDB(PDFDocumentBase):
    id: Optional[Union[str, PyObjectId]] = None
    file_url: str
    uploaded_by: PyObjectId
    created_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class PDFAssignmentRequest(BaseModel):
    pdf_id: str
    user_ids: list[str] 