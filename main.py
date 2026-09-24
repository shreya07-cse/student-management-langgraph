from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud, database
from chatbot import ask_chatbot

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Student Management System with AI Integration")

# CRUD Endpoints
@app.post("/students/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(database.get_db)):
    return crud.create_student(db=db, student=student)

@app.get("/students/", response_model=List[schemas.StudentResponse])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_students(db=db, skip=skip, limit=limit)

@app.get("/students/{student_id}", response_model=schemas.StudentResponse)
def read_student(student_id: int, db: Session = Depends(database.get_db)):
    db_student = crud.get_student(db=db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@app.put("/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(database.get_db)):
    updated_student = crud.update_student(db=db, student_id=student_id, student_data=student)
    if updated_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated_student

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_student(db=db, student_id=student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student record deleted successfully"}

# AI Chatbot Endpoint
@app.post("/chat/")
def chat_with_database(user_query: str):
    answer = ask_chatbot(user_query)
    return {"query": user_query, "response": answer}