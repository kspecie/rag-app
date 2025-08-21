from typing import List
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .document_loader import load_documents
import re

def clean_document_content(documents: List[Document]) -> List[Document]:
    """
    cleans list of uploaded documents
    """
    cleaned_documents = []
    for doc in documents:
        text = doc.page_content
        # remove newlines and extra spaces
        text = re.sub(r'\n{2,}', '\n', text)
        text = re.sub(r'\s{2,}', ' ', text)

        #strip leading whitespace
        text = text.strip()

        #update doc with the cleaned content
        doc.page_content = text
        cleaned_documents.append(doc)

    print(f"{len(cleaned_documents)} documents have been cleaned.")

    return cleaned_documents

def split_documents_into_chunks(
    documents: List[Document],
    chunk_size: int = 450,
    chunk_overlap: int = 150,
    add_start_index: bool = True
) -> List[Document]:
    """
    Splits a list of LangChain Document objects into smaller, overlapping chunks.
    Returns:
        List[Document]: A list of smaller LangChain Document objects (chunks).
    """
   
    print(f"Splitting {len(documents)} documents into chunks...")
    print(f"Chunk size: {chunk_size}, Chunk overlap: {chunk_overlap}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=add_start_index
    )

    all_splits: List[Document] = []

    for doc in documents:
        # Split this document into chunks
        doc_chunks = text_splitter.split_documents([doc])

        for chunk in doc_chunks:
            #Preserve all parent metadata
            chunk.metadata = {**doc.metadata, **chunk.metadata}

            # Always ensure 'source' is set to filename (not full path)
            if "file_name" in chunk.metadata:
                chunk.metadata["source"] = chunk.metadata["file_name"]
            else:
                # Always clean the source field to extract filename from path if needed
                source = chunk.metadata.get("source", "")
                if "/" in source or "\\" in source:
                    chunk.metadata["source"] = source.split("/")[-1].split("\\")[-1]

            all_splits.append(chunk)

    print(f"Original documents split into {len(all_splits)} chunks.")
    return all_splits
