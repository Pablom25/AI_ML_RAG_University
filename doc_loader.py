from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from pathlib import Path
import re

def _infer_meta_from_path(p: Path):
    """
    Expect paths like:
      data/students/Alejandro/*.txt
      data/university/*.txt
    """
    parts = [x.lower() for x in p.parts]

    # ----------------------------
    # STUDENT DOCUMENTS
    # ----------------------------
    if "students" in parts:
        i = parts.index("students")
        student = p.parts[i+1].lower()

        stem = p.stem.lower()

        # Identify document type
        if "cv" in stem:
            doc_type = "cv"
        elif "essay" in stem:
            doc_type = "admission_essay"
        elif "recommend" in stem:
            doc_type = "recommendation_letter"
        else:
            doc_type = stem  # fallback for unknown types

        return {
            "scope": "student",
            "student": student.replace(" ", "").replace("_", ""),
            "doc_type": doc_type,
            "source_path": str(p)
        }

    # ----------------------------
    # UNIVERSITY DOCUMENTS
    # ----------------------------
    return {
        "scope": "university",
        "doc_type": p.stem.lower(),
        "source_path": str(p)
    }

def doc_loader(path:str, persist_dir: str = "chroma", force_reload=False) -> Chroma | None:
    '''Takes data path, loads it, splits it, embeds it, and returns the vector store'''

    # Embedding function
    embedding = OllamaEmbeddings(model="mxbai-embed-large")

    # Check if vectorstore already created
    if Path(persist_dir).exists() and any(Path(persist_dir).iterdir()) and not force_reload:
        print(f"Using existing Chroma DB found at '{persist_dir}'.")
        db = Chroma(persist_directory=persist_dir, embedding_function=embedding)
        return db

    # If vectorstore doesn't exist, create it
    loader = DirectoryLoader(
        path,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    print("docs:", len(docs))

    # Insert metadata
    for d in docs:
        meta = _infer_meta_from_path(Path(d.metadata.get("source", "")))
        d.metadata.update(meta)

    # Split
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
    chunks = splitter.split_documents(docs)
    print("chunks:", len(chunks))

    # Add id
    for i, c in enumerate(chunks):
        c.metadata.setdefault("chunk_id", i)
    
    # Embed
    db = Chroma.from_documents(chunks, embedding, persist_directory=persist_dir)
    print(f"New Chroma DB created at '{persist_dir}'.")
    return db

if __name__ == "__main__":
    doc_loader("data")
