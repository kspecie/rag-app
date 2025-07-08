from typing import List, Dict, Any
from langchain.schema import Document
import requests
import json

def create_embeddings(chunks: List[Document], tei_service_url: str) -> List[Dict[str, Any]]:
    """
    Generates embeddings for a list of LangChain Document objects using the TEI service.
    Returns a list of dictionaries, each containing 'text', 'metadata', and 'embedding'.
    """
    print(f"Sending {len(chunks)} chunks to TEI service for embedding...")
    
    texts_to_embed = [chunk.page_content for chunk in chunks]
    
    headers = {"Content-Type": "application/json"}
    payload = {"inputs": texts_to_embed} # TEI expects a list of strings
    
    try:
        response = requests.post(f"{tei_service_url}/embed", headers=headers, data=json.dumps(payload), timeout=300)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        embeddings = response.json()

        if not isinstance(embeddings, list) or not all(isinstance(e, list) for e in embeddings):
            raise ValueError("TEI service returned an unexpected format for embeddings.")

        # Combine original chunks with their embeddings
        embedded_data = []
        for i, chunk in enumerate(chunks):
            embedded_data.append({
                "text": chunk.page_content,
                "metadata": chunk.metadata,
                "embedding": embeddings[i]
            })
        print(f"Successfully generated embeddings for {len(embedded_data)} chunks.")
        return embedded_data

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to TEI service at {tei_service_url}: {e}")
        return []

    except Exception as e:
        print(f"An unexpected error occurred during embedding: {e}")
        return []

# if __name__ == "__main__":
#     # This block won't run directly without some dummy data
#     print("This module is meant to be imported and used by main.py or other pipeline scripts.")
#     print("Please run main.py or add dummy data for direct testing.")
    # Example dummy usage:
    # from langchain.schema import Document
    # dummy_chunks = [
    #     Document(page_content="This is the first sentence.", metadata={"source": "test"}),
    #     Document(page_content="This is the second sentence.", metadata={"source": "test"}),
    # ]
    # TEI_URL = os.getenv("TEI_SERVICE_URL", "http://tei_service:80")
    # embedded = create_embeddings(dummy_chunks, TEI_URL)
    # print(f"Embedded dummy: {embedded[:1]}") # Print first one for brevity