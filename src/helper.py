
from typing import List
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

#  Document Processing Helpers
def load_data_file(data_path: str) -> List[Document]:
    """
    Load all PDF files from a directory and return LangChain Document objects.
    """
    loader = DirectoryLoader(
        data_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    return documents

#    Extracting content and source
def extract_page_content_and_source(docs: List[Document]) -> List[Document]:
    """
    Ensure each document has its page content and metadata with source.
    """
    final_docs = []
    for doc in docs:
        src = doc.metadata.get("source", "unknown")
        final_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": src}
            )
        )
    return final_docs


#   Splitting documents into chunks

def split_documents(docs: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Split documents into smaller chunks suitable for embedding + FAISS.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    return chunks

#  Loading Embedding Model


def load_embedding_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> HuggingFaceEmbeddings:
    """
    Initialize a HuggingFace embedding model compatible with LangChain + FAISS.
    """
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)
    return embedding_model

