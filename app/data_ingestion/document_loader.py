import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.schema import Document

def load_documents(directory_path: str) -> List[Document]:
    """
    using LangChain's DirectoryLoader to load all file types (currently .pdf and .txt)
    Args:
        directory_path (str): The path to the directory containing the documents.
    Returns:
        List[Document]: A list of LangChain Document objects.
    """
    # Ensure the directory exists
    if not Path(directory_path).is_dir():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    # Define the loader mapping for different file types
    loader_mapping = {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
        # ".docx": Docx2txtLoader,
        # ".csv": CSVLoader,
    }

    # Initialize the DirectoryLoader
    loader = DirectoryLoader(
        path=directory_path,
        glob="**/*",  # This pattern matches all files recursively
        use_multithreading=True,
        show_progress=True,
        silent_errors=True,
    )

    print(f"Loading documents from: {directory_path}...")
    documents = loader.load()
    print(f"Loaded {len(documents)} documents.")

    return documents

if __name__ == "__main__":
    loaded_docs = load_documents("/rag-app/data/raw_data")