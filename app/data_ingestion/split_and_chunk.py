from typing import List

from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .document_loader import load_documents

def split_documents_into_chunks(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
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

    all_splits = text_splitter.split_documents(documents)

    print(f"Original documents split into {len(all_splits)} chunks.")
    return all_splits

# This block allows you to test the splitting functionality independently
if __name__ == "__main__":
   
    if loaded_docs:
        print(f"\n--- Documents loaded successfully. Proceeding to split ---")
        chunks = split_documents_into_chunks(loaded_docs)

        # Print some details of the first few chunks
        if chunks:
            for i, chunk in enumerate(chunks[:5]): # Print details for up to 5 chunks
                print(f"\n--- Chunk {i+1} (Length: {len(chunk.page_content)}) ---")
                print(f"Content:\n{chunk.page_content}")
                print(f"Metadata: {chunk.metadata}")
                if "start_index" in chunk.metadata:
                    print(f"Start Index: {chunk.metadata['start_index']}")
        else:
            print("No chunks were generated.")
    else:
        print("no documents to split")
    