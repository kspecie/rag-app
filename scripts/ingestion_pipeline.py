# import os
# from app.data_ingestion.document_loader import load_documents
# from app.data_ingestion.split_and_chunk import split_documents_into_chunks
# from app.embed_and_store.embed import get_tei_instance
# from app.embed_and_store.embed import generate_embeddings
# from app.embed_and_store.store import setup_vector_store
# from langchain.docstore.document import Document

# RAW_DATA_FOLDER="/rag_app/data/raw_data"

# def run_ingestion_pipeline():
#     print("---starting run_ingestion_pipeline---")
#     #Step1: Load documents
#     try:
#         print("---running load_documents---")
#         loaded_documents = load_documents(RAW_DATA_FOLDER)
        
#         if not loaded_documents:
#             print("No documents loaded. Exiting")
#             return
#     except FileNotFoundError as e:
#         print(f"Error: {e}")
#         print("Please ensure the 'raw_data' directory exists and is accessible.")
#         return
#     #Step 2: Split into Chunks
#     print("---splitting documents into chunks---")
#     document_chunks = split_documents_into_chunks(loaded_documents)
#     print("---run_ingestion_pipeline complete---")
#     #Step 3: Initialize embedding model
#     print("start embedder")
#     embedder = get_tei_instance()
#     #Step 4: Generate Embeddings (optional - standalone)
#     #embeddings = generate_embeddings(document_chunks, embedder)
#     #print(f"Sample embedding (first 5 dims): {embeddings[0][:5]}")
#     #Step 5: Store in vector database
#     print("start store in vector db")
#     store = setup_vector_store(embedder)
#     # Convert chunks into Document objects
#     docs = document_chunks
#     # Add documents (embedding + store)
#     store.add_documents(docs)

#     print(f"Stored {len(docs)} documents in the vector store.")
    
# if __name__ == "__main__":
#     run_ingestion_pipeline()