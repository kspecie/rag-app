import chromadb
from typing import List, Dict, Any

def retrieve_relevant_chunks(
    query: str,
    chroma_db_url: str,
    n_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Retrieves and re-ranks the top N most relevant chunks from all available ChromaDB collections.
    """
    all_retrieved_chunks = []

    try:
        # Connect to the ChromaDB client
        client = chromadb.HttpClient(
            host=chroma_db_url.split('://')[1].split(':')[0],
            port=int(chroma_db_url.split(':')[-1])
        )

        collections = client.list_collections()
        print(f"🔍 Found collections: {[col.name for col in collections]}")

        for col in collections:
            collection = client.get_collection(name=col.name)

            results = collection.query(
                query_texts=[query],
                n_results=n_results * 2,
                include=['documents', 'metadatas', 'distances']
            )

            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    distance = results['distances'][0][i]
                    # Check if the distance is not None before appending
                    if distance is not None:
                        all_retrieved_chunks.append({
                            "page_content": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i],
                            "distance": distance,
                            "source_collection": col.name
                        })

        # Sort all chunks by their distance (relevance) score
        # A smaller distance value means higher relevance
        all_retrieved_chunks.sort(key=lambda x: x['distance'])
        
        # Return only the top n_results from the combined, sorted list
        final_chunks = all_retrieved_chunks[:n_results]

        print(f"✅ Found and re-ranked {len(final_chunks)} total chunks across collections.")
        return final_chunks

    except Exception as e:
        print(f"Error retrieving from ChromaDB: {e}")
        return []


# import chromadb
# from typing import List, Dict, Any

# def retrieve_relevant_chunks(
#     query: str,
#     chroma_db_url: str,
#     n_results: int = 10
# ) -> List[Dict[str, Any]]:
#     """
#     Retrieves the top_n most relevant chunks from all available ChromaDB collections for a given query.

#     Args:
#         query (str): The user's query or prompt.
#         chroma_db_url (str): The URL of the ChromaDB service (e.g., "http://chromadb:8000").
#         n_results (int): Total number of relevant chunks to retrieve across all collections.

#     Returns:
#         List[Dict[str, Any]]: A list of dictionaries, each with 'page_content', 'metadata', and 'source_collection'.
#     """
#     relevant_chunks = []

#     try:
#         # Connect to the ChromaDB client
#         client = chromadb.HttpClient(
#             host=chroma_db_url.split('://')[1].split(':')[0],
#             port=int(chroma_db_url.split(':')[-1])
#         )

#         # Get all available collection names
#         collections = client.list_collections()
#         print(f"🔍 Found collections: {[col.name for col in collections]}")

#         for col in collections:
#             collection = client.get_collection(name=col.name)

#             results = collection.query(
#                 query_texts=[query],
#                 n_results=n_results,
#                 include=['documents', 'metadatas']
#             )

#             if results and results['documents']:
#                 for i in range(len(results['documents'][0])):
#                     chunk_content = results['documents'][0][i]
#                     chunk_metadata = results['metadatas'][0][i]
#                     relevant_chunks.append({
#                         "page_content": chunk_content,
#                         "metadata": chunk_metadata,
#                         "source_collection": col.name
#                     })

#         return relevant_chunks[:n_results]

#     except Exception as e:
#         print(f"Error retrieving from ChromaDB: {e}")
#         return []
