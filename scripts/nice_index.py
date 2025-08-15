# import os
# import requests
# import chromadb
# import json
# from chromadb.utils import embedding_functions

# # --- Configuration ---
# CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
# CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
# TEI_HOST = os.getenv("TEI_HOST", "tei_service")
# TEI_PORT = os.getenv("TEI_PORT", "80")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# # NICE API config (placeholder)
# NICE_API_KEY = os.getenv("NICE_API_KEY", "your_api_key_here") 
# NICE_API_BASE_URL = "https://api.nice.org.uk"
# SAFE_PAYLOAD_LIMIT_BYTES = 500000
# MAX_DOCS_PER_BATCH = 16

# # --- Initialize Clients ---
# try:
#     chroma_client = chromadb.HttpClient(
#         host=CHROMA_HOST,
#         port=CHROMA_PORT
#     )
#     print(f"Connected to ChromaDB at http://{CHROMA_HOST}:{CHROMA_PORT}")

#     def tei_embedding_function(texts):
#         tei_url = f"http://{TEI_HOST}:{TEI_PORT}/embed"
#         response = requests.post(tei_url, json={"inputs": texts})
#         response.raise_for_status()
#         return response.json()

# except requests.exceptions.RequestException as e:
#     print(f"Error connecting to a service: {e}")
#     exit(1)

# # --- NICE API Logic ---
# def fetch_nice_guidance_index():
#     print("Fetching NICE guidance index from API...")
#     headers = {
#         "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
#         "API-Key": NICE_API_KEY
#     }
#     api_url = f"{NICE_API_BASE_URL}/services/guidance/ifp/index"
    
#     try:
#         response = requests.get(api_url, headers=headers)
#         response.raise_for_status()
#         data = response.json()
#         print("\n--- Raw JSON Response from API ---")
#         print(json.dumps(data, indent=2))
#         print("----------------------------------\n")
#         print("data:", data)
#         print("Top-level keys in data:", data.keys())

#         items = data.get("IndexItems", [])
#         if not isinstance(items, list):
#             print(f"Unexpected NICE API structure: {type(items)}")
#             return []

#         all_guidance_numbers = []
#         for item in items:
#             guidance_number = item.get("GuidanceNumber")
#             uri = item.get("Link", {}).get("Uri")
#             if guidance_number and uri:
#                 all_guidance_numbers.append({
#                     "guidance_number": guidance_number,
#                     "uri": f"{NICE_API_BASE_URL}{uri}"
#                     })
                
#         print(f"successfully fetched {len(all_guidance_numbers)} guidance numbers")
#         print(f"all guidance list: {all_guidance_numbers}")
#         return all_guidance_numbers
        
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching index from NICE API: {e}")
#         return []

# def fetch_full_document_content(doc_uri):
#     """
#     Fetches the full content of a single document by following its unique URI.
#     """
#     # This is the corrected line to append the final part of the path
#     full_doc_url = f"{doc_uri}/full-document" if doc_uri.startswith("http") \
#                     else f"{NICE_API_BASE_URL}{doc_uri}/full-document"
    
#     headers = {
#         "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
#         "API-Key": NICE_API_KEY
#     }
    
#     try:
#         print(f"  -> Downloading full content from {full_doc_url}")
#         response = requests.get(full_doc_url, headers=headers)
#         response.raise_for_status()
        
#         full_content_data = response.json()
        
#         content = full_content_data.get('Content', '')
#         return content
    
#     except requests.exceptions.RequestException as e:
#         print(f"Error downloading full content from {full_doc_url}: {e}")
#         return ""


# # --- Main Indexing Logic ---
# def index_nice_knowledge():
#     collection_name = "nice_knowledge"

#     try:
#         collection = chroma_client.get_collection(name=collection_name)
#         print(f"Collection '{collection_name}' already exists. Skipping indexing.")
#         count = collection.count()
#         print(f"Collection '{collection_name}' contains {count} documents.")

#         if count > 0:
#             ids_to_get = collection.get()['ids'][:2]
#             sample_documents = collection.get(ids=ids_to_get, include=['documents'])
            
#             print("\nDisplaying summaries for the first 2 documents:")
#             for i, doc_id in enumerate(sample_documents['ids']):
#                 document_content = sample_documents['documents'][i]
#                 lines = document_content.split('\n')
#                 title = lines[0].replace('Title: ', '')
#                 summary = lines[1].replace('Summary: ', '')
                
#                 print(f"  Document {i+1} (ID: {doc_id}):")
#                 print(f"    Title: {title}")
#                 print(f"    Summary: {summary}\n")
#         else:
#             print("No documents found in the collection to display.")
        
#         return
#     except chromadb.errors.NotFoundError:
#         print(f"Collection '{collection_name}' not found. Creating and indexing...")

#     collection = chroma_client.create_collection(
#         name=collection_name,
#         # Set embedding_function to None here if you are using TEI
#         embedding_function=None 
#     )

#     # Fetch document links from API
#     doc_links = fetch_nice_guidance_index()
#     if not doc_links:
#         print("No document links found. Exiting.")
#         return

#     processed_data = []
#     for doc in doc_links:
#         doc_uri = doc.get("uri")
#         doc_id = doc.get("guidance_number")
#         doc_title = doc_id  # Replace with actual title if available

#         if doc_uri:
#             summary_content = fetch_full_document_content(doc_uri)
#             if summary_content:
#                 processed_data.append({
#                     "id": doc_id,
#                     "title": doc_title,
#                     "summary": summary_content
#                 })

#     if not processed_data:
#         print("No full documents found to index.")
#         return

#     # Use the correct variable name here: 'processed_data'
#     total_docs = len(processed_data)
#     current_batch_docs = []
#     current_batch_ids = []
#     current_payload_size = 0
#     document_counter = 0

#     # This is the main indexing loop
#     for entry in processed_data:
#         document = f"Title: {entry['title']}\nSummary: {entry['summary']}"
#         doc_id = entry["id"]
#         doc_size = len(json.dumps(document))
        
#         # --- Batching logic ---
#         if (current_payload_size + doc_size > SAFE_PAYLOAD_LIMIT_BYTES) or (len(current_batch_docs) >= MAX_DOCS_PER_BATCH):
#             if current_batch_docs:
#                 try:
#                     embeddings = tei_embedding_function(current_batch_docs)
#                     collection.add(
#                         documents=current_batch_docs,
#                         embeddings=embeddings,
#                         ids=current_batch_ids
#                     )
#                     print(f"Ingested {document_counter} / {total_docs} documents.")
#                 except requests.exceptions.HTTPError as e:
#                     print(f"Error getting embeddings from TEI: {e}")
#                     raise e
            
#             current_batch_docs = [document]
#             current_batch_ids = [doc_id]
#             current_payload_size = doc_size
#         else:
#             current_batch_docs.append(document)
#             current_batch_ids.append(doc_id)
#             current_payload_size += doc_size

#         document_counter += 1

#     # Final batch
#     if current_batch_docs:
#         try:
#             embeddings = tei_embedding_function(current_batch_docs)
#             collection.add(
#                 documents=current_batch_docs,
#                 embeddings=embeddings,
#                 ids=current_batch_ids
#             )
#             print(f"Ingested {document_counter} / {total_docs} documents.")
#         except requests.exceptions.HTTPError as e:
#             print(f"Error (final batch): {e}")
#             raise e

#     print(f"\nIndexing complete! The '{collection_name}' collection is ready to use.")

#     # Verify collection contents
#     print("\nVerifying the collection contents...")
#     try:
#         count = collection.count()
#         print(f"Total documents in '{collection_name}': {count}")
        
#         if count > 0:
#             ids_to_get = collection.get()['ids'][:2]
#             sample_documents = collection.get(ids=ids_to_get, include=['documents'])
            
#             print("\nDisplaying summaries for the first 2 documents:")
#             for i, doc_id in enumerate(sample_documents['ids']):
#                 document_content = sample_documents['documents'][i]
#                 lines = document_content.split('\n')
#                 title = lines[0].replace('Title: ', '')
#                 summary = lines[1].replace('Summary: ', '')
                
#                 print(f"  Document {i+1} (ID: {doc_id}):")
#                 print(f"    Title: {title}")
#                 print(f"    Summary: {summary}\n")
#         else:
#             print("No documents found in the collection to display.")
#     except Exception as e:
#         print(f"Error verifying collection: {e}")

# if __name__ == "__main__":
#     index_nice_knowledge()

# import os
# import requests
# import chromadb
# import json
# import textwrap # New import for robust chunking
# from chromadb.utils import embedding_functions

# # --- Configuration ---
# CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
# CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
# TEI_HOST = os.getenv("TEI_HOST", "tei_service")
# TEI_PORT = os.getenv("TEI_PORT", "80")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# # NICE API config
# NICE_API_KEY = os.getenv("NICE_API_KEY", "your_api_key_here") 
# NICE_API_BASE_URL = "https://api.nice.org.uk"

# # Adjusted payload limit to a very conservative value
# # TEI service limit is often around 500kb. Let's use 100kb as a safe margin.
# SAFE_PAYLOAD_LIMIT_BYTES = 100000 
# MAX_DOCS_PER_BATCH = 16

# # --- Initialize Clients ---
# try:
#     chroma_client = chromadb.HttpClient(
#         host=CHROMA_HOST,
#         port=CHROMA_PORT
#     )
#     print(f"Connected to ChromaDB at http://{CHROMA_HOST}:{CHROMA_PORT}")

#     def tei_embedding_function(texts):
#         tei_url = f"http://{TEI_HOST}:{TEI_PORT}/embed"
#         response = requests.post(tei_url, json={"inputs": texts})
#         response.raise_for_status()
#         return response.json()

# except requests.exceptions.RequestException as e:
#     print(f"Error connecting to a service: {e}")
#     exit(1)

# # --- NICE API Logic ---
# def fetch_nice_guidance_index():
#     print("Fetching NICE guidance index from API...")
#     headers = {
#         "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
#         "API-Key": NICE_API_KEY
#     }
#     api_url = f"{NICE_API_BASE_URL}/services/guidance/ifp/index"
    
#     try:
#         response = requests.get(api_url, headers=headers)
#         response.raise_for_status()
#         data = response.json()

#         items = data.get("IndexItems", [])
#         if not isinstance(items, list):
#             print(f"Unexpected NICE API structure: {type(items)}")
#             return []

#         all_guidance_numbers = []
#         for item in items:
#             guidance_number = item.get("GuidanceNumber")
#             uri = item.get("Link", {}).get("Uri")
#             if guidance_number and uri:
#                 all_guidance_numbers.append({
#                     "guidance_number": guidance_number,
#                     "uri": f"{NICE_API_BASE_URL}{uri}"
#                 })
        
#         print(f"Successfully fetched {len(all_guidance_numbers)} guidance numbers")
#         return all_guidance_numbers
        
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching index from NICE API: {e}")
#         return []

# def fetch_full_document_content(doc_uri):
#     """
#     Fetches the full content of a single document by following its unique URI.
#     """
#     full_doc_url = f"{doc_uri}/full-document" if doc_uri.startswith("http") \
#                     else f"{NICE_API_BASE_URL}{doc_uri}/full-document"
    
#     headers = {
#         "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
#         "API-Key": NICE_API_KEY
#     }
    
#     try:
#         print(f"  -> Downloading full content from {full_doc_url}")
#         response = requests.get(full_doc_url, headers=headers)
#         response.raise_for_status()
        
#         full_content_data = response.json()
        
#         content = full_content_data.get('Content', '')
#         return content
    
#     except requests.exceptions.RequestException as e:
#         print(f"Error downloading full content from {full_doc_url}: {e}")
#         return ""

# # New and improved chunking function
# def chunk_text(text, max_chunk_size_bytes):
#     """
#     Splits a single string into a list of chunks based on a maximum size in bytes,
#     maintaining sentence integrity.
#     """
#     # Max chunk size in characters is a safe bet, assuming UTF-8
#     max_chunk_size_chars = int(max_chunk_size_bytes / 4) 
    
#     chunks = textwrap.wrap(text, width=max_chunk_size_chars, break_long_words=False, break_on_hyphens=False)
    
#     final_chunks = []
#     # Ensure no chunk exceeds the byte size limit
#     for chunk in chunks:
#         if len(chunk.encode('utf-8')) > max_chunk_size_bytes:
#             # Fallback to a brute force split if textwrap fails
#             sub_chunks = [chunk[i:i+max_chunk_size_chars] for i in range(0, len(chunk), max_chunk_size_chars)]
#             final_chunks.extend(sub_chunks)
#         else:
#             final_chunks.append(chunk)

#     return final_chunks

# # --- Main Indexing Logic ---
# def index_nice_knowledge():
#     collection_name = "nice_knowledge"

#     try:
#         collection = chroma_client.get_collection(name=collection_name)
#         print(f"Collection '{collection_name}' already exists. Skipping indexing.")
#         count = collection.count()
#         print(f"Collection '{collection_name}' contains {count} documents.")
#         return
#     except chromadb.errors.NotFoundError:
#         print(f"Collection '{collection_name}' not found. Creating and indexing...")

#     collection = chroma_client.create_collection(
#         name=collection_name,
#         embedding_function=None 
#     )

#     doc_links = fetch_nice_guidance_index()
#     if not doc_links:
#         print("No document links found. Exiting.")
#         return

#     processed_chunks = []
#     for doc in doc_links:
#         doc_uri = doc.get("uri")
#         doc_id = doc.get("guidance_number")
#         doc_title = doc_id
        
#         if doc_uri:
#             content = fetch_full_document_content(doc_uri)
#             if not content:
#                 continue

#             document_text = f"Title: {doc_title}\nSummary: {content}"
#             chunks = chunk_text(document_text, SAFE_PAYLOAD_LIMIT_BYTES)
            
#             for i, chunk in enumerate(chunks):
#                 processed_chunks.append({
#                     "id": f"{doc_id}_{i}",
#                     "text": chunk
#                 })

#     if not processed_chunks:
#         print("No full documents found to index.")
#         return

#     total_chunks = len(processed_chunks)
#     current_batch_docs = []
#     current_batch_ids = []
#     current_payload_size = 0
#     chunk_counter = 0

#     for entry in processed_chunks:
#         doc_text = entry["text"]
#         doc_id = entry["id"]
#         doc_size = len(doc_text.encode('utf-8'))

#         if (current_payload_size + doc_size > SAFE_PAYLOAD_LIMIT_BYTES) or (len(current_batch_docs) >= MAX_DOCS_PER_BATCH):
#             if current_batch_docs:
#                 try:
#                     embeddings = tei_embedding_function(current_batch_docs)
#                     collection.add(
#                         documents=current_batch_docs,
#                         embeddings=embeddings,
#                         ids=current_batch_ids
#                     )
#                     print(f"Ingested {len(current_batch_docs)} chunks. Total so far: {chunk_counter}.")
#                 except requests.exceptions.HTTPError as e:
#                     print(f"Error getting embeddings from TEI: {e}")
#                     raise e
            
#             current_batch_docs = [doc_text]
#             current_batch_ids = [doc_id]
#             current_payload_size = doc_size
#         else:
#             current_batch_docs.append(doc_text)
#             current_batch_ids.append(doc_id)
#             current_payload_size += doc_size

#         chunk_counter += 1

#     if current_batch_docs:
#         try:
#             embeddings = tei_embedding_function(current_batch_docs)
#             collection.add(
#                 documents=current_batch_docs,
#                 embeddings=embeddings,
#                 ids=current_batch_ids
#             )
#             print(f"Ingested final batch of {len(current_batch_docs)} documents. Total: {chunk_counter}")
#         except requests.exceptions.HTTPError as e:
#             print(f"Error (final batch): {e}")
#             raise e

#     print(f"\nIndexing complete! The '{collection_name}' collection is ready to use.")

# if __name__ == "__main__":
#     index_nice_knowledge()


#The below version works but the chunks are too large which impacts retrieval.
# import os
# import requests
# import chromadb
# import json
# import textwrap 
# from chromadb.utils import embedding_functions
# import time

# # --- Configuration ---
# CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
# CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
# TEI_HOST = os.getenv("TEI_HOST", "tei_service")
# TEI_PORT = os.getenv("TEI_PORT", "80")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# # NICE API config
# NICE_API_KEY = os.getenv("NICE_API_KEY", "your_api_key_here") 
# NICE_API_BASE_URL = "https://api.nice.org.uk"

# # limits to avoid 413 errors
# SAFE_PAYLOAD_LIMIT_BYTES = 50000  
# MAX_DOCS_PER_BATCH = 8           
# MAX_CHUNK_SIZE_BYTES = 8000     

# # --- Initialize Clients ---
# try:
#     chroma_client = chromadb.HttpClient(
#         host=CHROMA_HOST,
#         port=CHROMA_PORT
#     )
#     print(f"Connected to ChromaDB at http://{CHROMA_HOST}:{CHROMA_PORT}")

#     def tei_embedding_function(texts):
#         """Enhanced embedding function with retry logic and better error handling"""
#         tei_url = f"http://{TEI_HOST}:{TEI_PORT}/embed"
        
#         # Log payload size for debugging
#         total_chars = sum(len(text) for text in texts)
#         total_bytes = sum(len(text.encode('utf-8')) for text in texts)
#         print(f"    Embedding batch: {len(texts)} docs, {total_chars} chars, {total_bytes} bytes")
        
#         max_retries = 3
#         for attempt in range(max_retries):
#             try:
#                 response = requests.post(tei_url, json={"inputs": texts}, timeout=120)
#                 response.raise_for_status()
#                 return response.json()
#             except requests.exceptions.HTTPError as e:
#                 if e.response.status_code == 413:
#                     print(f"    Payload too large error on attempt {attempt + 1}")
#                     if attempt < max_retries - 1:
#                         # If we still have retries, split the batch further
#                         if len(texts) == 1:
#                             print(f"    Single document still too large: {len(texts[0])} chars")
#                             raise e
#                         # Split batch in half and retry each half
#                         mid = len(texts) // 2
#                         print(f"    Splitting batch: {len(texts)} -> {mid} + {len(texts) - mid}")
#                         first_half = tei_embedding_function(texts[:mid])
#                         second_half = tei_embedding_function(texts[mid:])
#                         return first_half + second_half
#                     else:
#                         raise e
#                 else:
#                     raise e
#             except requests.exceptions.RequestException as e:
#                 print(f"    Request error on attempt {attempt + 1}: {e}")
#                 if attempt < max_retries - 1:
#                     time.sleep(2 ** attempt)  # Exponential backoff
#                 else:
#                     raise e

# except requests.exceptions.RequestException as e:
#     print(f"Error connecting to a service: {e}")
#     exit(1)

# # --- NICE API Logic ---
# def fetch_nice_guidance_index():
#     print("Fetching NICE guidance index from API...")
#     headers = {
#         "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
#         "API-Key": NICE_API_KEY
#     }
#     api_url = f"{NICE_API_BASE_URL}/services/guidance/ifp/index"
    
#     try:
#         response = requests.get(api_url, headers=headers)
#         response.raise_for_status()
#         data = response.json()

#         items = data.get("IndexItems", [])
#         if not isinstance(items, list):
#             print(f"Unexpected NICE API structure: {type(items)}")
#             return []

#         all_guidance_numbers = []
#         for item in items:
#             guidance_number = item.get("GuidanceNumber")
#             uri = item.get("Link", {}).get("Uri")
#             if guidance_number and uri:
#                 all_guidance_numbers.append({
#                     "guidance_number": guidance_number,
#                     "uri": f"{NICE_API_BASE_URL}{uri}"
#                 })
        
#         print(f"Successfully fetched {len(all_guidance_numbers)} guidance numbers")
#         return all_guidance_numbers
        
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching index from NICE API: {e}")
#         return []

# def fetch_full_document_content(doc_uri):
#     """
#     Fetches the full content of a single document by following its unique URI.
#     """
#     full_doc_url = f"{doc_uri}/full-document" if doc_uri.startswith("http") \
#                     else f"{NICE_API_BASE_URL}{doc_uri}/full-document"
    
#     headers = {
#         "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
#         "API-Key": NICE_API_KEY
#     }
    
#     try:
#         print(f"  -> Downloading full content from {full_doc_url}")
#         response = requests.get(full_doc_url, headers=headers)
#         response.raise_for_status()
        
#         full_content_data = response.json()
        
#         content = full_content_data.get('Content', '')
#         return content
    
#     except requests.exceptions.RequestException as e:
#         print(f"Error downloading full content from {full_doc_url}: {e}")
#         return ""

# def chunk_text(text, max_chunk_size_bytes):
#     """
#     Splits a single string into a list of chunks based on a maximum size in bytes,
#     maintaining sentence integrity.
#     """
#     if not text or not text.strip():
#         return []
    
#     # Convert bytes to characters (conservative estimate for UTF-8)
#     max_chunk_size_chars = int(max_chunk_size_bytes / 4)
    
#     # First try to split by paragraphs
#     paragraphs = text.split('\n\n')
#     chunks = []
#     current_chunk = ""
    
#     for paragraph in paragraphs:
#         # If adding this paragraph would exceed the limit
#         if len((current_chunk + "\n\n" + paragraph).encode('utf-8')) > max_chunk_size_bytes:
#             if current_chunk:
#                 chunks.append(current_chunk.strip())
#                 current_chunk = paragraph
#             else:
#                 # Single paragraph is too large, split it
#                 para_chunks = textwrap.wrap(
#                     paragraph, 
#                     width=max_chunk_size_chars, 
#                     break_long_words=False, 
#                     break_on_hyphens=False
#                 )
#                 chunks.extend(para_chunks)
#         else:
#             if current_chunk:
#                 current_chunk += "\n\n" + paragraph
#             else:
#                 current_chunk = paragraph
    
#     if current_chunk:
#         chunks.append(current_chunk.strip())
    
#     # Final check: ensure no chunk exceeds byte limit
#     final_chunks = []
#     for chunk in chunks:
#         chunk_bytes = len(chunk.encode('utf-8'))
#         if chunk_bytes > max_chunk_size_bytes:
#             # Brute force split if still too large
#             chars_per_chunk = int(max_chunk_size_bytes / 4)  # Conservative estimate
#             sub_chunks = [chunk[i:i+chars_per_chunk] for i in range(0, len(chunk), chars_per_chunk)]
#             final_chunks.extend([sc for sc in sub_chunks if sc.strip()])
#         else:
#             final_chunks.append(chunk)

#     return [chunk for chunk in final_chunks if chunk.strip()]

# def safe_batch_embed(collection, documents, ids):
#     """
#     Safely embed and add documents with adaptive batch sizing.
#     """
#     if not documents:
#         return
    
#     # Start with a small batch size and increase if successful
#     batch_size = min(4, len(documents))  # Start very conservative
#     i = 0
    
#     while i < len(documents):
#         batch_docs = documents[i:i + batch_size]
#         batch_ids = ids[i:i + batch_size]
        
#         # Calculate batch size
#         batch_bytes = sum(len(doc.encode('utf-8')) for doc in batch_docs)
        
#         try:
#             embeddings = tei_embedding_function(batch_docs)
#             collection.add(
#                 documents=batch_docs,
#                 embeddings=embeddings,
#                 ids=batch_ids
#             )
#             print(f"  Successfully embedded batch of {len(batch_docs)} docs ({batch_bytes} bytes)")
#             i += batch_size
            
#             # If successful and batch was small, try increasing size next time
#             if batch_size < MAX_DOCS_PER_BATCH and batch_bytes < SAFE_PAYLOAD_LIMIT_BYTES // 2:
#                 batch_size = min(batch_size + 2, MAX_DOCS_PER_BATCH)
                
#         except requests.exceptions.HTTPError as e:
#             if e.response.status_code == 413:
#                 print(f"  Batch too large ({batch_bytes} bytes), reducing size")
#                 # Reduce batch size
#                 batch_size = max(1, batch_size // 2)
#                 if batch_size == 1 and len(batch_docs) == 1:
#                     # Single document is still too large, skip it
#                     print(f"  Skipping oversized document: {batch_ids[0]} ({batch_bytes} bytes)")
#                     i += 1
#                     batch_size = 4  # Reset for next batch
#             else:
#                 raise e

# # --- Main Indexing Logic ---
# def index_nice_knowledge():
#     collection_name = "nice_knowledge"

#     try:
#         collection = chroma_client.get_collection(name=collection_name)
#         print(f"Collection '{collection_name}' already exists. Skipping indexing.")
#         count = collection.count()
#         print(f"Collection '{collection_name}' contains {count} documents.")
#         return
#     except chromadb.errors.NotFoundError:
#         print(f"Collection '{collection_name}' not found. Creating and indexing...")

#     collection = chroma_client.create_collection(
#         name=collection_name,
#         embedding_function=None 
#     )

#     doc_links = fetch_nice_guidance_index()
#     if not doc_links:
#         print("No document links found. Exiting.")
#         return

#     processed_chunks = []
#     total_docs = len(doc_links)
    
#     for idx, doc in enumerate(doc_links):
#         doc_uri = doc.get("uri")
#         doc_id = doc.get("guidance_number")
#         doc_title = doc_id
        
#         print(f"Processing document {idx + 1}/{total_docs}: {doc_id}")
        
#         if doc_uri:
#             content = fetch_full_document_content(doc_uri)
#             if not content:
#                 print(f"  No content found for {doc_id}")
#                 continue

#             document_text = f"Title: {doc_title}\nSummary: {content}"
#             chunks = chunk_text(document_text, MAX_CHUNK_SIZE_BYTES)
            
#             print(f"  Created {len(chunks)} chunks")
            
#             for i, chunk in enumerate(chunks):
#                 chunk_bytes = len(chunk.encode('utf-8'))
#                 if chunk_bytes > MAX_CHUNK_SIZE_BYTES:
#                     print(f"  Warning: Chunk {i} still oversized: {chunk_bytes} bytes")
                
#                 processed_chunks.append({
#                     "id": f"{doc_id}_{i}",
#                     "text": chunk
#                 })
        
#         # Process in smaller batches to avoid memory issues
#         if len(processed_chunks) >= 50:  # Process every 50 chunks
#             print(f"Processing batch of {len(processed_chunks)} chunks...")
#             documents = [chunk["text"] for chunk in processed_chunks]
#             ids = [chunk["id"] for chunk in processed_chunks]
#             safe_batch_embed(collection, documents, ids)
#             processed_chunks = []  # Clear processed chunks

#     # Process remaining chunks
#     if processed_chunks:
#         print(f"Processing final batch of {len(processed_chunks)} chunks...")
#         documents = [chunk["text"] for chunk in processed_chunks]
#         ids = [chunk["id"] for chunk in processed_chunks]
#         safe_batch_embed(collection, documents, ids)

#     final_count = collection.count()
#     print(f"\nIndexing complete! The '{collection_name}' collection contains {final_count} documents.")

# if __name__ == "__main__":
#     index_nice_knowledge()

import os
import requests
import chromadb
import json
import re
from typing import List, Dict, Any
import hashlib

# --- Configuration ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
TEI_HOST = os.getenv("TEI_HOST", "tei_service")
TEI_PORT = os.getenv("TEI_PORT", "80")

# NICE API config
NICE_API_KEY = os.getenv("NICE_API_KEY", "your_api_key_here") 
NICE_API_BASE_URL = "https://api.nice.org.uk"

# Hierarchical chunking settings
MAX_SECTION_TOKENS = 800    # Sections that fit in context with room for query+response
MAX_SUMMARY_TOKENS = 200    # Document summaries
OVERLAP_TOKENS = 50         # Overlap between adjacent chunks for context

class DocumentProcessor:
    def __init__(self):
        self.chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    def tei_embedding_function(self, texts):
        tei_url = f"http://{TEI_HOST}:{TEI_PORT}/embed"
        response = requests.post(tei_url, json={"inputs": texts})
        response.raise_for_status()
        return response.json()
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        return len(text) // 3
    
    def extract_document_structure(self, content: str, doc_id: str) -> Dict[str, Any]:
        """
        Extract structured information from NICE guidance document.
        This attempts to identify key sections common in NICE documents.
        """
        
        # Common NICE document sections (adjust based on your actual document structure)
        section_patterns = [
            r"(?i)^(summary|executive summary|key recommendations?)",
            r"(?i)^(recommendations?)",
            r"(?i)^(introduction|background)",
            r"(?i)^(scope|who is it for)",
            r"(?i)^(methodology|methods?)",
            r"(?i)^(evidence|evidence review)",
            r"(?i)^(clinical considerations?)",
            r"(?i)^(implementation|putting this guideline into practice)",
            r"(?i)^(research recommendations?)",
            r"(?i)^(appendix|appendices)"
        ]
        
        lines = content.split('\n')
        sections = []
        current_section = {"title": "Introduction", "content": "", "start_line": 0}
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                current_section["content"] += "\n"
                continue
            
            # Check if this line is a section header
            is_section_header = False
            for pattern in section_patterns:
                if re.match(pattern, line):
                    is_section_header = True
                    break
            
            # Also check for numbered sections (1., 2., etc.) or lettered sections
            if not is_section_header:
                if re.match(r'^\d+\.?\s+[A-Z]', line) or re.match(r'^[A-Z]\.\s+[A-Z]', line):
                    is_section_header = True
            
            if is_section_header and current_section["content"].strip():
                # Save previous section
                sections.append(current_section)
                # Start new section
                current_section = {
                    "title": line,
                    "content": "",
                    "start_line": i
                }
            else:
                current_section["content"] += line + "\n"
        
        # Don't forget the last section
        if current_section["content"].strip():
            sections.append(current_section)
        
        # If no sections found, treat whole document as one section
        if not sections:
            sections = [{
                "title": f"Complete Document",
                "content": content,
                "start_line": 0
            }]
        
        return {
            "doc_id": doc_id,
            "sections": sections,
            "total_tokens": self.estimate_tokens(content)
        }
    
    def create_document_summary(self, content: str, doc_id: str, title: str) -> str:
        """
        Create a concise summary of the document for high-level retrieval.
        """
        # Extract first few sentences or paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        summary_parts = [f"NICE Guidance {doc_id}: {title}"]
        current_tokens = self.estimate_tokens(summary_parts[0])
        
        for para in paragraphs[:5]:  # First few paragraphs
            para_tokens = self.estimate_tokens(para)
            if current_tokens + para_tokens > MAX_SUMMARY_TOKENS:
                break
            summary_parts.append(para)
            current_tokens += para_tokens
        
        summary = "\n\n".join(summary_parts)
        
        # If still too long, truncate
        if self.estimate_tokens(summary) > MAX_SUMMARY_TOKENS:
            chars_to_keep = MAX_SUMMARY_TOKENS * 3
            summary = summary[:chars_to_keep] + "..."
        
        return summary
    
    def create_focused_chunks(self, section: Dict[str, Any], doc_id: str, doc_title: str) -> List[Dict[str, Any]]:
        """
        Create smaller, focused chunks from a document section while preserving context.
        """
        section_title = section["title"]
        content = section["content"]
        
        if self.estimate_tokens(content) <= MAX_SECTION_TOKENS:
            # Section fits in one chunk
            full_context = f"Document: {doc_title} ({doc_id})\nSection: {section_title}\n\n{content}"
            return [{
                "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}",
                "text": full_context,
                "type": "section",
                "section_title": section_title
            }]
        
        # Split large section into smaller chunks with overlap
        chunks = []
        sentences = content.split('. ')
        current_chunk = ""
        chunk_num = 0
        
        for i, sentence in enumerate(sentences):
            test_chunk = current_chunk + (". " + sentence if current_chunk else sentence)
            
            if self.estimate_tokens(test_chunk) <= MAX_SECTION_TOKENS - 100:  # Reserve space for context
                current_chunk = test_chunk
            else:
                if current_chunk.strip():
                    # Create chunk with full context
                    context_header = f"Document: {doc_title} ({doc_id})\nSection: {section_title}\nPart {chunk_num + 1}:\n\n"
                    chunk_text = context_header + current_chunk
                    
                    chunks.append({
                        "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
                        "text": chunk_text,
                        "type": "section_chunk",
                        "section_title": section_title,
                        "part_number": chunk_num
                    })
                    
                    # Start new chunk with overlap (last few sentences)
                    overlap_sentences = sentences[max(0, i-2):i]  # Include previous 2 sentences for context
                    current_chunk = ". ".join(overlap_sentences + [sentence])
                    chunk_num += 1
                else:
                    current_chunk = sentence
        
        # Don't forget the last chunk
        if current_chunk.strip():
            context_header = f"Document: {doc_title} ({doc_id})\nSection: {section_title}\nPart {chunk_num + 1}:\n\n"
            chunk_text = context_header + current_chunk
            
            chunks.append({
                "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
                "text": chunk_text,
                "type": "section_chunk",
                "section_title": section_title,
                "part_number": chunk_num
            })
        
        return chunks
    
    def process_document(self, doc_uri: str, doc_id: str, doc_title: str) -> List[Dict[str, Any]]:
        """
        Process a single NICE document into hierarchical chunks.
        """
        print(f"  Processing {doc_id}...")
        
        # Download content
        content = self.fetch_full_document_content(doc_uri)
        if not content:
            return []
        
        all_chunks = []
        
        # 1. Create document summary (for high-level matching)
        summary = self.create_document_summary(content, doc_id, doc_title)
        all_chunks.append({
            "id": f"{doc_id}_summary",
            "text": summary,
            "type": "summary",
            "doc_title": doc_title
        })
        
        # 2. Extract document structure
        doc_structure = self.extract_document_structure(content, doc_id)
        
        # 3. Process each section
        for section in doc_structure["sections"]:
            section_chunks = self.create_focused_chunks(section, doc_id, doc_title)
            all_chunks.extend(section_chunks)
        
        print(f"    Created {len(all_chunks)} chunks ({len(doc_structure['sections'])} sections)")
        return all_chunks
    
    def fetch_full_document_content(self, doc_uri):
        """Fetch document content from NICE API"""
        full_doc_url = f"{doc_uri}/full-document" if doc_uri.startswith("http") \
                        else f"{NICE_API_BASE_URL}{doc_uri}/full-document"
        
        headers = {
            "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
            "API-Key": NICE_API_KEY
        }
        
        try:
            response = requests.get(full_doc_url, headers=headers)
            response.raise_for_status()
            full_content_data = response.json()
            return full_content_data.get('Content', '')
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {doc_uri}: {e}")
            return ""

def index_nice_knowledge_hierarchical():
    """
    Index NICE knowledge with hierarchical structure preservation.
    """
    processor = DocumentProcessor()
    collection_name = "nice_knowledge_hierarchical"
    
    try:
        collection = processor.chroma_client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists. Skipping indexing.")
        return
    except chromadb.errors.NotFoundError:
        print(f"Collection '{collection_name}' not found. Creating...")
    
    collection = processor.chroma_client.create_collection(
        name=collection_name,
        embedding_function=None
    )
    

    doc_links = fetch_nice_guidance_index() 
    if not doc_links:
        print("No documents found.")
        return
    
    total_chunks = 0
    for i, doc in enumerate(doc_links):
        print(f"Document {i+1}/{len(doc_links)}: {doc['guidance_number']}")
        
        chunks = processor.process_document(
            doc['uri'], 
            doc['guidance_number'], 
            doc['guidance_number']
        )
        
        if chunks:
            # Batch embed and store
            texts = [chunk["text"] for chunk in chunks]
            ids = [chunk["id"] for chunk in chunks]
            metadata = [{"type": chunk.get("type", "unknown"), 
                        "doc_id": doc['guidance_number']} for chunk in chunks]
            
            try:
                embeddings = processor.tei_embedding_function(texts)
                collection.add(
                    documents=texts,
                    embeddings=embeddings,
                    ids=ids,
                    metadatas=metadata
                )
                total_chunks += len(chunks)
                print(f"    Added {len(chunks)} chunks")
            except Exception as e:
                print(f"    Error embedding chunks: {e}")
    
    print(f"Indexing complete! {total_chunks} chunks in collection.")

def fetch_nice_guidance_index():
    print("Fetching NICE guidance index from API...")
    headers = {
        "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
        "API-Key": NICE_API_KEY
    }
    api_url = f"{NICE_API_BASE_URL}/services/guidance/ifp/index"
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        items = data.get("IndexItems", [])
        if not isinstance(items, list):
            print(f"Unexpected NICE API structure: {type(items)}")
            return []

        all_guidance_numbers = []
        for item in items:
            guidance_number = item.get("GuidanceNumber")
            uri = item.get("Link", {}).get("Uri")
            if guidance_number and uri:
                all_guidance_numbers.append({
                    "guidance_number": guidance_number,
                    "uri": f"{NICE_API_BASE_URL}{uri}"
                })
        
        print(f"Successfully fetched {len(all_guidance_numbers)} guidance numbers")
        return all_guidance_numbers
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching index from NICE API: {e}")
        return []


if __name__ == "__main__":
    index_nice_knowledge_hierarchical()