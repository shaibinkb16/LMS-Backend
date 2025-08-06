from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Union
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {'type': 'string'}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "employee"  # admin or employee

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: Optional[str] = None
    created_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True

class UserInDB(UserBase):
    id: Optional[str] = None
    password_hash: str
    created_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str}
        from_attributes = True 