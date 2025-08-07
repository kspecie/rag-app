import os
import chromadb
from typing import List, Dict, Any

def retrieve_relevant_chunks(
    query: str,
    chroma_db_url: str,
    collection_name: str,
    n_results: int = 10
) -> List[Dict[str, Any]]:
    """
     Retrieves the top_n most relevant chunks from ChromaDB for a given query.

    Args:
        query (str): The user's query or prompt.
        chroma_db_url (str): The URL of the ChromaDB service (e.g., "http://chromadb:8000").
        collection_name (str): The name of the collection to query.
        n_results (int): The number of relevant chunks to retrieve.
     Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                               represents a retrieved chunk with 'page_content' and 'metadata'.
    
    """
    try:
        # Connect to the ChromaDB client
        client = chromadb.HttpClient(host=chroma_db_url.split('://')[1].split(':')[0], port=int(chroma_db_url.split(':')[-1]))
        collection = client.get_or_create_collection(name=collection_name)

        # Query the collection
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents', 'metadatas'] # Request documents (content) and metadatas
        )

        relevant_chunks = []
        if results and results['documents']:
            # results['documents'] will be a list of lists if multiple queries were made.
            # We made one query, so we take the first sublist.
            for i in range(len(results['documents'][0])):
                chunk_content = results['documents'][0][i]
                chunk_metadata = results['metadatas'][0][i]
                relevant_chunks.append({
                    "page_content": chunk_content,
                    "metadata": chunk_metadata
                })
        return relevant_chunks

    except Exception as e:
        print(f"Error retrieving from ChromaDB: {e}")
        return []