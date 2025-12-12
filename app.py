
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain imports
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Local imports
from src.helper import load_embedding_model
from src.prompt import prompt   # ChatPromptTemplate

#   INITIAL SETUP

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML templates
templates = Jinja2Templates(directory="templates")

# Environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not found in environment.")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY or ""

# Load embedding model
embedding = load_embedding_model()

#   Load FAISS Index

FAISS_INDEX_DIR = "faiss_index" 
if not os.path.exists(FAISS_INDEX_DIR):
    raise RuntimeError(f"FAISS index not found in '{FAISS_INDEX_DIR}'. Run store_index.py first.")

vector_store = FAISS.load_local(FAISS_INDEX_DIR, embeddings=embedding,    
                                allow_dangerous_deserialization=True
)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

#   Language Model (Groq)


llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile"
)
model = llm  

#  Documents Chain Implementation

def format_docs(docs):
    try:
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        logger.exception("Error formatting docs: %s", e)
        return ""

QA_chain = (
    {
        "context": lambda x: format_docs(x["context"]),
        "question": lambda x: x["question"]
    }
    | prompt
    | model
)

#  RAG PIPELINE Setup

rag_chain = (
    {
        "question": RunnablePassthrough(),
        "context": retriever
    }
    | QA_chain
    | StrOutputParser()
)

# ROUTES

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat_api(request_data: ChatRequest):
    try:
        user_question = request_data.query
        result = rag_chain.invoke(user_question)
        return {"answer": str(result)}
    except Exception as e:
        logger.exception("Error in /chat endpoint: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error. Please try again.")


# Production Entrypoint for Uvicorn/Render


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
