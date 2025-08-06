# def delete_document_by_name(
#     chroma_service_url: str,
#     document_name: str,
#     collection_name: str = "rag_documents"
# ):
#     """
#     Deletes all chunks from ChromaDB for the given document name.
#     """
#     try:
#         client = chromadb.HttpClient(host=chroma_service_url.replace("http://", "").split(":")[0], port=8000)
#         collection = client.get_or_create_collection(name=collection_name)

#         print(f"Deleting chunks for document: {document_name}")
#         collection.delete(where={"source": document_name})
#         print(f"All chunks for '{document_name}' deleted successfully.")
#     except Exception as e:
#         print(f"Error deleting document: {e}")
