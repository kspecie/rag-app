import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.schema import Document
from datetime import datetime

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
    # loader_mapping = {
    #     ".txt": TextLoader,
    #     ".pdf": PyPDFLoader,
    #     # ".docx": Docx2txtLoader,
    #     # ".csv": CSVLoader,
    # }
    supported_extensions = {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
    }

    loaded_documents = []


    # return documents
    print(f"Loading documents from: {directory_path}...")

    for file_path in Path(directory_path).rglob("*"):
        ext = file_path.suffix.lower()
        if ext in supported_extensions:
            loader_class = supported_extensions[ext]
            try:
                # Load the document(s)
                loader = loader_class(str(file_path))
                docs = loader.load()

                # Inject filename into metadata
                for doc in docs:
                    doc.metadata["file_name"] = file_path.name
                    doc.metadata["source"] = file_path.name  # Set source to filename, not full path
                    doc.metadata["upload_date"] = datetime.now().isoformat()
                    loaded_documents.append(doc)

            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")

    print(f"Loaded {len(loaded_documents)} documents with filenames in metadata.")
    return loaded_documents

if __name__ == "__main__":
    loaded_docs = load_documents("/rag-app/data/raw_data")