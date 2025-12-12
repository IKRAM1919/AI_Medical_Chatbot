import os
from src.helper import (
    load_data_file,
    extract_page_content_and_source,
    split_documents,
    load_embedding_model,
)
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_ACCESS_TOKEN = os.getenv("HUGGINGFACE_ACCESS_TOKEN")
if HUGGINGFACE_ACCESS_TOKEN:
    os.environ["HUGGINGFACE_ACCESS_TOKEN"] = HUGGINGFACE_ACCESS_TOKEN

DATA_DIR = "data"
INDEX_DIR = "faiss_index"

print("Loading documents...")
documents = load_data_file(DATA_DIR)
print(f"{len(documents)} documents loaded")

documents = extract_page_content_and_source(documents)
print("Extracted page content and source.")

chunks = split_documents(documents)
print(f"{len(chunks)} chunks created")

print("Loading embedding model...")
embeddings = load_embedding_model()
print(f"Embedding model loaded: {embeddings}")

print("Building FAISS index...")
faiss_index = FAISS.from_documents(chunks, embeddings)

os.makedirs(INDEX_DIR, exist_ok=True)
faiss_index.save_local(INDEX_DIR)

print(f"FAISS index created and saved to '{INDEX_DIR}' with {len(chunks)} chunks.")
