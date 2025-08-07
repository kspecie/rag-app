from typing import List, Dict, Any
from langchain.schema import Document
import requests
import time
import json

MAX_PAYLOAD_BYTES = 1_900_000  # TEI's default limit
MAX_TEI_BATCH_ITEMS = 32 #Maximum number of chunks allowed per batch by the TEI service

def batch_chunks_by_payload_size_and_count(
    chunks: List[Document], 
    max_bytes: int = MAX_PAYLOAD_BYTES,
    max_items: int = MAX_TEI_BATCH_ITEMS
) -> List[List[Document]]:
    """
    Batches LangChain Document chunks so that each batch adheres to:
    1. A maximum estimated total JSON payload size.
    2. A maximum number of items (chunks) per batch.
    """
    batches = []
    current_batch_documents = [] # Store actual Document objects
    
    for chunk in chunks:
        # Check item count first
        if len(current_batch_documents) >= max_items:
            if current_batch_documents: # Only append if there's something in the batch
                batches.append(current_batch_documents)
            current_batch_documents = [] # Start a new batch

        # check payload size for the (potentially new) current batch
        temp_texts_for_estimation = [doc.page_content for doc in current_batch_documents] + [chunk.page_content]
        estimated_payload = json.dumps({"inputs": temp_texts_for_estimation}).encode("utf-8")
        estimated_total_payload_size = len(estimated_payload)

        if estimated_total_payload_size > max_bytes:
            if current_batch_documents: # Only append if there's something in the batch
                batches.append(current_batch_documents)
            
            # Start a new batch with the current chunk
            current_batch_documents = [chunk]
            
            # Critical check: if a single chunk is larger than MAX_PAYLOAD_BYTES
            if len(json.dumps({"inputs": [chunk.page_content]}).encode("utf-8")) > max_bytes:
                print(f"WARNING: A single chunk is larger than MAX_PAYLOAD_BYTES ({max_bytes} bytes). "
                      "This chunk will likely fail to embed. Consider increasing max_bytes on TEI or reducing chunk size.")

        else:
            # If it fits both item count and size, add the chunk to the current batch
            current_batch_documents.append(chunk)

    # Add any remaining chunks as the last batch
    if current_batch_documents:
        batches.append(current_batch_documents)

    return batches

def create_embeddings(chunks: List[Document], tei_service_url: str) -> List[Dict[str, Any]]:
    """
    Generates embeddings for a list of LangChain Document objects using the TEI service.
    Batches the requests to avoid payload size and item count errors.
    
    Returns a list of dictionaries, each containing 'text', 'metadata', and 'embedding'.
    """

    all_embeddings = [] 
    # Pass the new max_items argument
    batches = batch_chunks_by_payload_size_and_count(chunks, max_bytes=MAX_PAYLOAD_BYTES, max_items=MAX_TEI_BATCH_ITEMS)

    print(f"Sending {len(chunks)} chunks to TEI service for embedding (total batches: {len(batches)})...")
    if not batches:
        print("No batches created. This might indicate an issue with chunking or payload limits.")
        return []

    headers = {"Content-Type": "application/json"}

    for batch_num, batch_documents in enumerate(batches):
        texts_to_embed = [chunk.page_content for chunk in batch_documents]
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

            if len(embeddings) != len(texts_to_embed):
                raise ValueError(f"TEI service returned {len(embeddings)} embeddings for {len(texts_to_embed)} texts in batch {batch_num}.")

            for i, chunk in enumerate(batch_documents):
                all_embeddings.append({
                    "text": chunk.page_content,
                    "metadata": chunk.metadata,
                    "embedding": embeddings[i]
                })
            print(f"Successfully processed batch {batch_num} with {len(batch_documents)} chunks. Current total embeddings: {len(all_embeddings)}")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error for batch {batch_num} ({len(batch_documents)} chunks): {http_err} - Response: {http_err.response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error for batch {batch_num} ({len(batch_documents)} chunks): {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error for batch {batch_num} ({len(batch_documents)} chunks): {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An unexpected request error occurred for batch {batch_num} ({len(batch_documents)} chunks): {req_err}")
        except ValueError as val_err:
            print(f"Data validation error for batch {batch_num}: {val_err}")
        except Exception as e:
            print(f"An unexpected error occurred in batch {batch_num}: {e}")

        time.sleep(0.5) 

    print(f"Ingestion pipeline complete. Generated {len(all_embeddings)} embeddings.")
    return all_embeddings

