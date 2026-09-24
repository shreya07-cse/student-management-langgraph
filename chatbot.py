import os
import sqlite3
from typing import TypedDict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

load_dotenv()

# Initialize Gemini LLM via LangChain (Zero-cost free tier)
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash", 
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# 1. Define State Schema for LangGraph
class AgentState(TypedDict):
    user_query: str
    generated_sql: str
    db_results: str
    final_response: str

# 2. Database Helper Function
def query_database(sql_query: str):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    conn.close()
    return results

# Helper to cleanly extract text content from LangChain response objects
def extract_text(content) -> str:
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict):
                text_parts.append(part.get("text", ""))
            else:
                text_parts.append(str(part))
        return "".join(text_parts)
    return str(content)

# 3. Define LangGraph Nodes
def generate_sql_node(state: AgentState) -> dict:
    schema = """
    Table: students
    Columns: id (INTEGER), name (TEXT), email (TEXT), gender (TEXT), age (INTEGER), grade (TEXT), gpa (REAL)
    Note: Gender values are stored in lowercase ('male', 'female').
    """
    
    system_prompt = f"""
    You are a SQLite database expert. Convert the user's question into a valid, executable SQLite query.
    
    Schema:
    {schema}
    
    Rules:
    - Return ONLY the raw SQL query string.
    - Do NOT wrap in markdown, triple backticks, or quotes.
    - Use case-insensitive matches like LOWER(gender) = 'female'.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_query"])
    ]
    
    response = llm.invoke(messages)
    raw_text = extract_text(response.content)
    clean_sql = raw_text.strip().replace("```sql", "").replace("```", "").strip()
    
    print(f"[LANGGRAPH - Node 1] Generated SQL: {clean_sql}")
    return {"generated_sql": clean_sql}


def execute_sql_node(state: AgentState) -> dict:
    sql = state["generated_sql"]
    try:
        data = query_database(sql)
        print(f"[LANGGRAPH - Node 2] DB Result: {data}")
        return {"db_results": str(data)}
    except Exception as e:
        print(f"[LANGGRAPH - Node 2 Error]: {str(e)}")
        return {"db_results": f"Error executing query: {str(e)}"}


def generate_summary_node(state: AgentState) -> dict:
    prompt = f"""
    User Question: "{state['user_query']}"
    Executed SQL: "{state['generated_sql']}"
    Query Result Data: {state['db_results']}
    
    Provide a concise, direct answer in natural language based on the database output.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    final_text = extract_text(response.content).strip()
    
    print(f"[LANGGRAPH - Node 3] Final Summary Generated.")
    return {"final_response": final_text}


# 4. Construct LangGraph Workflow
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)
workflow.add_node("generate_summary", generate_summary_node)

# Add Edges (Linear Execution Flow)
workflow.set_entry_point("generate_sql")
workflow.add_edge("generate_sql", "execute_sql")
workflow.add_edge("execute_sql", "generate_summary")
workflow.add_edge("generate_summary", END)

# Compile Graph Application
app_graph = workflow.compile()


# 5. Main Entry Function called by FastAPI endpoint
def ask_chatbot(user_prompt: str) -> str:
    initial_state = {
        "user_query": user_prompt,
        "generated_sql": "",
        "db_results": "",
        "final_response": ""
    }
    
    # Run the stateful graph
    output_state = app_graph.invoke(initial_state)
    return output_state["final_response"]