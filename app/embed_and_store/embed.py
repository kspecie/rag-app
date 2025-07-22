from typing import List, Dict, Any
from langchain.schema import Document
import requests
import time
import json

def create_embeddings(chunks: List[Document], tei_service_url: str, batch_size: int = 10) -> List[Dict[str, Any]]:
    """
    Generates embeddings for a list of LangChain Document objects using the TEI service.
    Batches the requests to avoid payload size errors.
    
    Returns a list of dictionaries, each containing 'text', 'metadata', and 'embedding'.
    """
    print(f"Sending {len(chunks)} chunks to TEI service for embedding (batch size: {batch_size})...")
    headers = {"Content-Type": "application/json"}

    embedded_data = []

    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        batch = chunks[start:end]
        texts_to_embed = [doc.page_content for doc in batch]
        payload = {"inputs": texts_to_embed}

        try:
            response = requests.post(
                f"{tei_service_url}/embed",
                headers=headers,
                data=json.dumps(payload),
                timeout=300
            )
            response.raise_for_status()
            embeddings = response.json()

            if not isinstance(embeddings, list) or not all(isinstance(e, list) for e in embeddings):
                raise ValueError("TEI service returned an unexpected format for embeddings.")

            for i, doc in enumerate(batch):
                embedded_data.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "embedding": embeddings[i]
                })

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to TEI service at {tei_service_url} for batch {start}-{end}: {e}")
            continue

        except Exception as e:
            print(f"Unexpected error during embedding batch {start}-{end}: {e}")
            continue

        # Optional
        time.sleep(0.2)

    print(f"Successfully generated embeddings for {len(embedded_data)} chunks.")
    return embedded_data

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