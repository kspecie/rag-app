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
            # ✅ Preserve all parent metadata
            chunk.metadata = {**doc.metadata, **chunk.metadata}

            # ✅ Ensure 'source' is set to filename
            if "source" not in chunk.metadata and "file_name" in chunk.metadata:
                chunk.metadata["source"] = chunk.metadata["file_name"]

            all_splits.append(chunk)

    print(f"Original documents split into {len(all_splits)} chunks.")
    return all_splits

#     all_splits = text_splitter.split_documents(documents)

#     for chunk in all_splits:
#         if "source" not in chunk.metadata and "file_name" in chunk.metadata:
#             chunk.metadata["source"] = chunk.metadata["file_name"]

#         if "upload_date" not in chunk.metadata and "file_name" in chunk.metadata:
#             # Find matching doc by filename
#             parent_doc = next((doc for doc in documents if doc.metadata.get("file_name") == chunk.metadata["file_name"]), None)
#             if parent_doc and "upload_date" in parent_doc.metadata:
#                 chunk.metadata["upload_date"] = parent_doc.metadata["upload_date"]

#     print(f"Original documents split into {len(all_splits)} chunks.")
#     return all_splits


# if __name__ == "__main__":
   
#     if loaded_docs:
#         print(f"\n--- Documents loaded successfully. Proceeding to split ---")
#         cleaned_docs = [clean_document_content(doc) for doc in loaded_docs]
#         print(f"Documents have been cleaned. Proceeding to split...")
#         chunks = split_documents_into_chunks(cleaned_docs)

#         # Print some details of the first few chunks
#         if chunks:
#             for i, chunk in enumerate(chunks[:5]): # Print details for up to 5 chunks
#                 print(f"\n--- Chunk {i+1} (Length: {len(chunk.page_content)}) ---")
#                 print(f"Content:\n{chunk.page_content}")
#                 print(f"Metadata: {chunk.metadata}")
#                 if "start_index" in chunk.metadata:
#                     print(f"Start Index: {chunk.metadata['start_index']}")
#         else:
#             print("No chunks were generated.")
#     else:
#         print("no documents to split")
    