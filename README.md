# Student Database Management System with LangGraph Chatbot

A modular FastAPI backend application integrated with Gemini API and LangGraph to perform natural language SQL queries on a student database.

## Features & Requirements Compliance

1. **Modular Code Architecture**: Cleanly separated into `main.py`, `models.py`, `schemas.py`, `crud.py`, `database.py`, and `chatbot.py`.
2. **CRUD API Endpoints**: Full REST API implementation for Create, Read, Update, and Delete operations on students.
3. **Service Execution**: Running as an active web application service via Uvicorn.
4. **Interactive API Documentation**: Fully documented and accessible using FastAPI Swagger UI (`/docs`).
5. **AI Chatbot**: Text-to-SQL stateful computational graph using **LangGraph** and **Gemini 3.6 Flash**.
6. **Vector Database Selection**:
   - **Chosen Database**: **ChromaDB** / **FAISS**
   - **Justification**: ChromaDB is selected for this project architecture because it is lightweight, open-source, zero-cost, and runs locally. It provides similarity search and embedding storage for unstructured student documents, complimenting our structured relational SQLite database without requiring external paid cloud infrastructure.

## Setup & Running Locally

1. **Clone the repository**:
   ```bash
   git clone <your-github-repo-link>
   cd student_management_project