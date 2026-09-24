from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentBase(BaseModel):
    name: str
    email: EmailStr
    gender: str
    age: int
    grade: str
    gpa: float

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None
    gpa: Optional[float] = None

class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True