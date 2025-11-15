from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from pathlib import Path
import re

def _infer_meta_from_path(p: Path):
    """
    Expect paths like:
      data/students/Alejandro/essay.txt
      data/university/requirements/cs.txt
    Returns metadata
    """
    parts = [x.lower() for x in p.parts]
    if "students" in parts:
        i = parts.index("students")
        student = p.parts[i+1].lower() if i+1 < len(p.parts) else "unknown"
        stem = p.stem.lower()
        match = re.search(r'[_\-]?([A-Z][a-zA-Z]+AdmissionEssay|CV|RecommendationLetter)', stem)
        doc_type = match.group(1).lower() if match else stem.lower()
        return {"scope": "student", "student": student, "doc_type": doc_type, "source_path": str(p)}
    # university / general docs
    return {"scope": "university", "doc_type": p.stem.lower(), "source_path": str(p)}

def doc_loader(path:str) -> Chroma | None:
    '''Takes data path, loads it, splits it, embeds it, and returns the vector store'''

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

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
    chunks = splitter.split_documents(docs)
    print("chunks:", len(chunks))

    # Add id
    for i, c in enumerate(chunks):
        c.metadata.setdefault("chunk_id", i)
    
    # Embed
    embedding = OllamaEmbeddings(model="mxbai-embed-large")
    db = Chroma.from_documents(chunks, embedding, persist_directory="chroma")
    return db

if __name__ == "__main__":
    doc_loader("data")
