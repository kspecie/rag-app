import os
import chromadb
from typing import List, Dict, Any

def retrieve_relevant_chunks(
    query: str,
    chroma_db_url: str,
    n_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Retrieves the top_n most relevant chunks from ALL available collections in ChromaDB for a given query.

    Args:
        query (str): The user's query or prompt.
        chroma_db_url (str): The URL of the ChromaDB service (e.g., "http://chromadb:8000").
        n_results (int): The number of relevant chunks to retrieve.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                               represents a retrieved chunk with 'page_content', 'metadata', and 'collection_name'.
    """
    try:
        # Connect to the ChromaDB client
        client = chromadb.HttpClient(
            host=chroma_db_url.split('://')[1].split(':')[0],
            port=int(chroma_db_url.split(':')[-1])
        )

        # Get a list of all available collections
        collections = client.list_collections()

        if not collections:
            print("No collections found in ChromaDB.")
            return []

        all_results = []
        
        # Query each collection and combine the results
        for collection in collections:
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results, 
                    include=['documents', 'metadatas', 'distances']
                )

                if results and results['documents']:
                    # Iterate through the results from this collection
                    for i in range(len(results['documents'][0])):
                        # Add the collection name to the metadata for context
                        metadata_with_collection = results['metadatas'][0][i]
                        metadata_with_collection['collection_name'] = collection.name

                        all_results.append({
                            "page_content": results['documents'][0][i],
                            "metadata": metadata_with_collection,
                            "distance": results['distances'][0][i]  # Include distance for sorting
                        })
            except Exception as e:
                print(f"Error querying collection '{collection.name}': {e}")
                # Continue to the next collection if an error occurs with one
                continue

        if not all_results:
            return []

        # Sort all combined results by distance (lower distance is better/more relevant)
        all_results.sort(key=lambda x: x['distance'])

        # Return only the top n_results
        final_results = all_results[:n_results]

        # Clean up the output by removing the 'distance' key, as it's not part of the final return contract
        for result in final_results:
            del result['distance']

        return final_results

    except Exception as e:
        print(f"Error retrieving from ChromaDB: {e}")
        return []