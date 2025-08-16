# import os
# import sys
# import chromadb
# import requests
# import json
# import re
# import hashlib
# from typing import List, Dict, Any
# from datasets import load_dataset
# from chromadb.utils import embedding_functions

# # --- Configuration ---
# CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
# CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
# TEI_HOST = os.getenv("TEI_HOST", "tei_service")
# TEI_PORT = os.getenv("TEI_PORT", "80")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
# NICE_API_KEY = os.getenv("NICE_API_KEY", "") 
# NICE_API_BASE_URL = "https://api.nice.org.uk"

# # --- Common Utilities ---
# def get_chroma_client():
#     """Initializes and returns a ChromaDB client."""
#     try:
#         return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
#     except Exception as e:
#         print(f"Error connecting to ChromaDB: {e}")
#         sys.exit(1)

# def tei_embedding_function(texts: List[str]):
#     """Generates embeddings using the TEI service."""
#     try:
#         tei_url = f"http://{TEI_HOST}:{TEI_PORT}/embed"
#         response = requests.post(tei_url, json={"inputs": texts})
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Error getting embeddings from TEI: {e}")
#         raise e

# # --- Document Processor for NICE Knowledge ---
# # Hierarchical chunking settings
# MAX_SECTION_TOKENS = 800
# MAX_SUMMARY_TOKENS = 200
# OVERLAP_TOKENS = 50

# class DocumentProcessor:
#     def __init__(self, chroma_client):
#         self.chroma_client = chroma_client
    
#     def estimate_tokens(self, text: str) -> int:
#         """Estimate token count"""
#         return len(text) // 3
    
#     def extract_document_structure(self, content: str, doc_id: str) -> Dict[str, Any]:
#         """
#         Extract structured information from NICE guidance document.
#         This attempts to identify key sections common in NICE documents.
#         """
#         section_patterns = [
#             r"(?i)^(summary|executive summary|key recommendations?)",
#             r"(?i)^(recommendations?)",
#             r"(?i)^(introduction|background)",
#             r"(?i)^(scope|who is it for)",
#             r"(?i)^(methodology|methods?)",
#             r"(?i)^(evidence|evidence review)",
#             r"(?i)^(clinical considerations?)",
#             r"(?i)^(implementation|putting this guideline into practice)",
#             r"(?i)^(research recommendations?)",
#             r"(?i)^(appendix|appendices)"
#         ]
        
#         lines = content.split('\n')
#         sections = []
#         current_section = {"title": "Introduction", "content": "", "start_line": 0}
        
#         for i, line in enumerate(lines):
#             line = line.strip()
#             if not line:
#                 current_section["content"] += "\n"
#                 continue
            
#             is_section_header = False
#             for pattern in section_patterns:
#                 if re.match(pattern, line):
#                     is_section_header = True
#                     break
            
#             if not is_section_header:
#                 if re.match(r'^\d+\.?\s+[A-Z]', line) or re.match(r'^[A-Z]\.\s+[A-Z]', line):
#                     is_section_header = True
            
#             if is_section_header and current_section["content"].strip():
#                 sections.append(current_section)
#                 current_section = {
#                     "title": line,
#                     "content": "",
#                     "start_line": i
#                 }
#             else:
#                 current_section["content"] += line + "\n"
        
#         if current_section["content"].strip():
#             sections.append(current_section)
        
#         if not sections:
#             sections = [{
#                 "title": f"Complete Document",
#                 "content": content,
#                 "start_line": 0
#             }]
        
#         return {
#             "doc_id": doc_id,
#             "sections": sections,
#             "total_tokens": self.estimate_tokens(content)
#         }
    
#     def create_document_summary(self, content: str, doc_id: str, title: str) -> str:
#         """Create a concise summary of the document for high-level retrieval."""
#         paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
#         summary_parts = [f"NICE Guidance {doc_id}: {title}"]
#         current_tokens = self.estimate_tokens(summary_parts[0])
        
#         for para in paragraphs[:5]:
#             para_tokens = self.estimate_tokens(para)
#             if current_tokens + para_tokens > MAX_SUMMARY_TOKENS:
#                 break
#             summary_parts.append(para)
#             current_tokens += para_tokens
        
#         summary = "\n\n".join(summary_parts)
#         if self.estimate_tokens(summary) > MAX_SUMMARY_TOKENS:
#             chars_to_keep = MAX_SUMMARY_TOKENS * 3
#             summary = summary[:chars_to_keep] + "..."
        
#         return summary
    
#     def create_focused_chunks(self, section: Dict[str, Any], doc_id: str, doc_title: str) -> List[Dict[str, Any]]:
#         """
#         Create smaller, focused chunks from a document section while preserving context.
#         """
#         section_title = section["title"]
#         content = section["content"]
        
#         if self.estimate_tokens(content) <= MAX_SECTION_TOKENS:
#             full_context = f"Document: {doc_title} ({doc_id})\nSection: {section_title}\n\n{content}"
#             return [{
#                 "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}",
#                 "text": full_context,
#                 "type": "section",
#                 "section_title": section_title
#             }]
        
#         chunks = []
#         sentences = content.split('. ')
#         current_chunk = ""
#         chunk_num = 0
        
#         for i, sentence in enumerate(sentences):
#             test_chunk = current_chunk + (". " + sentence if current_chunk else sentence)
            
#             if self.estimate_tokens(test_chunk) <= MAX_SECTION_TOKENS - 100:
#                 current_chunk = test_chunk
#             else:
#                 if current_chunk.strip():
#                     context_header = f"Document: {doc_title} ({doc_id})\nSection: {section_title}\nPart {chunk_num + 1}:\n\n"
#                     chunk_text = context_header + current_chunk
#                     chunks.append({
#                         "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
#                         "text": chunk_text,
#                         "type": "section_chunk",
#                         "section_title": section_title,
#                         "part_number": chunk_num
#                     })
#                     overlap_sentences = sentences[max(0, i-2):i]
#                     current_chunk = ". ".join(overlap_sentences + [sentence])
#                     chunk_num += 1
#                 else:
#                     current_chunk = sentence
        
#         if current_chunk.strip():
#             context_header = f"Document: {doc_title} ({doc_id})\nSection: {section_title}\nPart {chunk_num + 1}:\n\n"
#             chunk_text = context_header + current_chunk
#             chunks.append({
#                 "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
#                 "text": chunk_text,
#                 "type": "section_chunk",
#                 "section_title": section_title,
#                 "part_number": chunk_num
#             })
        
#         return chunks
    
#     def process_document(self, doc_uri: str, doc_id: str, doc_title: str) -> List[Dict[str, Any]]:
#         """Process a single NICE document into hierarchical chunks."""
#         print(f"  Processing {doc_id}...")
        
#         content = self.fetch_full_document_content(doc_uri)
#         if not content:
#             return []
        
#         all_chunks = []
#         summary = self.create_document_summary(content, doc_id, doc_title)
#         all_chunks.append({
#             "id": f"{doc_id}_summary",
#             "text": summary,
#             "type": "summary",
#             "doc_title": doc_title
#         })
        
#         doc_structure = self.extract_document_structure(content, doc_id)
        
#         for section in doc_structure["sections"]:
#             section_chunks = self.create_focused_chunks(section, doc_id, doc_title)
#             all_chunks.extend(section_chunks)
        
#         print(f"    Created {len(all_chunks)} chunks ({len(doc_structure['sections'])} sections)")
#         return all_chunks
    
#     def fetch_full_document_content(self, doc_uri):
#         """Fetch document content from NICE API"""
#         full_doc_url = f"{doc_uri}/full-document" if doc_uri.startswith("http") \
#                         else f"{NICE_API_BASE_URL}{doc_uri}/full-document"
        
#         headers = {
#             "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
#             "API-Key": NICE_API_KEY
#         }
        
#         try:
#             response = requests.get(full_doc_url, headers=headers)
#             response.raise_for_status()
#             full_content_data = response.json()
#             return full_content_data.get('Content', '')
#         except requests.exceptions.RequestException as e:
#             print(f"Error downloading {doc_uri}: {e}")
#             return ""

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

# # --- Collection Management Actions ---
# def delete_collection(collection_name: str):
#     """Deletes a ChromaDB collection by name."""
#     try:
#         chroma_client = get_chroma_client()
#         chroma_client.delete_collection(name=collection_name)
#         print(f"Successfully deleted collection '{collection_name}'.")
#     except chromadb.errors.NotFoundError:
#         print(f"Collection '{collection_name}' not found. No action needed.")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")

# def index_miriad_dataset(chroma_client):
#     """Indexes the Miriad dataset into a ChromaDB collection."""
#     collection_name = "miriad_knowledge"
#     SAFE_PAYLOAD_LIMIT_BYTES = 500000
#     MAX_DOCS_PER_BATCH = 16

#     try:
#         chroma_client.get_collection(name=collection_name)
#         print(f"Collection '{collection_name}' already exists. Skipping indexing.")
#         return
#     except chromadb.errors.NotFoundError:
#         print(f"Collection '{collection_name}' not found. Creating and indexing...")

#     collection = chroma_client.create_collection(
#         name=collection_name,
#         embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
#     )

#     print("Loading Miriad dataset...")
#     try:
#         dataset = load_dataset("miriad/miriad-5.8M", split="train[:20000]")
#         print("Dataset loaded successfully.")
#     except Exception as e:
#         print(f"Failed to load dataset: {e}")
#         return

#     total_docs = len(dataset)
#     current_batch_docs = []
#     current_batch_ids = []
#     current_payload_size = 0
#     document_counter = 0

#     for i, row in enumerate(dataset):
#         document = f"Question: {row['question']}\nAnswer: {row['answer']}"
#         doc_id = f"miriad_{i}"
#         doc_size = len(json.dumps(document))

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
#             print(f"Error getting embeddings from TEI (final batch): {e}")
#             raise e

#     print("\nIndexing complete! The 'miriad_knowledge' collection is ready to use.")

# def index_nice_knowledge(chroma_client):
#     """Indexes the NICE knowledge into a ChromaDB collection."""
#     processor = DocumentProcessor(chroma_client)
#     collection_name = "nice_knowledge"
    
#     try:
#         collection = chroma_client.get_collection(name=collection_name)
#         print(f"Collection '{collection_name}' already exists. Skipping indexing.")
#         return
#     except chromadb.errors.NotFoundError:
#         print(f"Collection '{collection_name}' not found. Creating...")
    
#     collection = chroma_client.create_collection(
#         name=collection_name,
#         embedding_function=None
#     )

#     doc_links = fetch_nice_guidance_index() 
#     if not doc_links:
#         print("No documents found.")
#         return
    
#     total_chunks = 0
#     for i, doc in enumerate(doc_links):
#         print(f"Document {i+1}/{len(doc_links)}: {doc['guidance_number']}")
        
#         chunks = processor.process_document(
#             doc['uri'], 
#             doc['guidance_number'], 
#             doc['guidance_number']
#         )
        
#         if chunks:
#             texts = [chunk["text"] for chunk in chunks]
#             ids = [chunk["id"] for chunk in chunks]
#             metadata = [{"type": chunk.get("type", "unknown"), 
#                         "doc_id": doc['guidance_number']} for chunk in chunks]
            
#             try:
#                 embeddings = tei_embedding_function(texts)
#                 collection.add(
#                     documents=texts,
#                     embeddings=embeddings,
#                     ids=ids,
#                     metadatas=metadata
#                 )
#                 total_chunks += len(chunks)
#                 print(f"    Added {len(chunks)} chunks")
#             except Exception as e:
#                 print(f"    Error embedding chunks: {e}")
    
#     print(f"Indexing complete! {total_chunks} chunks in collection.")


# # --- Command Line Interface ---
# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Usage: python manage_collections.py <action> <collection_name>")
#         print("Actions: delete, index")
#         sys.exit(1)

#     action = sys.argv[1].lower()
#     collection_to_act_on = sys.argv[2]
    
#     client = get_chroma_client()

#     if action == "delete":
#         delete_collection(collection_to_act_on)
#     elif action == "index":
#         if collection_to_act_on == "miriad_knowledge":
#             index_miriad_dataset(client)
#         elif collection_to_act_on == "nice_knowledge":
#             index_nice_knowledge(client)
#         else:
#             print(f"Error: Indexing for '{collection_to_act_on}' is not defined.")
#             sys.exit(1)
#     else:
#         print(f"Error: Unknown action '{action}'. Use 'delete' or 'index'.")
#         sys.exit(1)

import os
import sys
import chromadb
import requests
import json
import re
import hashlib
from typing import List, Dict, Any
from datasets import load_dataset
from chromadb.utils import embedding_functions

# --- Configuration ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
TEI_HOST = os.getenv("TEI_HOST", "tei_service")
TEI_PORT = os.getenv("TEI_PORT", "80")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
NICE_API_KEY = os.getenv("NICE_API_KEY", "") 
NICE_API_BASE_URL = "https://api.nice.org.uk"

# Collection name mapping (Frontend display name -> ChromaDB collection name)
COLLECTION_MAPPING = {
    "Miriad Knowledge": "miriad_knowledge",
    "Nice Knowledge": "nice_knowledge",
    "My Documents": "documents"
}

# --- Common Utilities ---
def get_chroma_client():
    """Initializes and returns a ChromaDB client."""
    try:
        return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        sys.exit(1)

def tei_embedding_function(texts: List[str]):
    """Generates embeddings using the TEI service."""
    try:
        tei_url = f"http://{TEI_HOST}:{TEI_PORT}/embed"
        response = requests.post(tei_url, json={"inputs": texts})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting embeddings from TEI: {e}")
        raise e

# --- Document Processor for NICE Knowledge ---
# Hierarchical chunking settings
MAX_SECTION_TOKENS = 800
MAX_SUMMARY_TOKENS = 200
OVERLAP_TOKENS = 50

class DocumentProcessor:
    def __init__(self, chroma_client):
        self.chroma_client = chroma_client
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        return len(text) // 3
    
    def extract_document_structure(self, content: str, doc_id: str) -> Dict[str, Any]:
        """
        Extract structured information from NICE guidance document.
        This attempts to identify key sections common in NICE documents.
        """
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
            
            is_section_header = False
            for pattern in section_patterns:
                if re.match(pattern, line):
                    is_section_header = True
                    break
            
            if not is_section_header:
                if re.match(r'^\d+\.?\s+[A-Z]', line) or re.match(r'^[A-Z]\.\s+[A-Z]', line):
                    is_section_header = True
            
            if is_section_header and current_section["content"].strip():
                sections.append(current_section)
                current_section = {
                    "title": line,
                    "content": "",
                    "start_line": i
                }
            else:
                current_section["content"] += line + "\n"
        
        if current_section["content"].strip():
            sections.append(current_section)
        
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
        """Create a concise summary of the document for high-level retrieval."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        summary_parts = [f"NICE Guidance {doc_id}: {title}"]
        current_tokens = self.estimate_tokens(summary_parts[0])
        
        for para in paragraphs[:5]:
            para_tokens = self.estimate_tokens(para)
            if current_tokens + para_tokens > MAX_SUMMARY_TOKENS:
                break
            summary_parts.append(para)
            current_tokens += para_tokens
        
        summary = "\n\n".join(summary_parts)
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
            full_context = f"Document: {doc_title} ({doc_id})\nSection: {section_title}\n\n{content}"
            return [{
                "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}",
                "text": full_context,
                "type": "section",
                "section_title": section_title
            }]
        
        chunks = []
        sentences = content.split('. ')
        current_chunk = ""
        chunk_num = 0
        
        for i, sentence in enumerate(sentences):
            test_chunk = current_chunk + (". " + sentence if current_chunk else sentence)
            
            if self.estimate_tokens(test_chunk) <= MAX_SECTION_TOKENS - 100:
                current_chunk = test_chunk
            else:
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
                    overlap_sentences = sentences[max(0, i-2):i]
                    current_chunk = ". ".join(overlap_sentences + [sentence])
                    chunk_num += 1
                else:
                    current_chunk = sentence
        
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
        """Process a single NICE document into hierarchical chunks."""
        print(f"  Processing {doc_id}...")
        
        content = self.fetch_full_document_content(doc_uri)
        if not content:
            return []
        
        all_chunks = []
        summary = self.create_document_summary(content, doc_id, doc_title)
        all_chunks.append({
            "id": f"{doc_id}_summary",
            "text": summary,
            "type": "summary",
            "doc_title": doc_title
        })
        
        doc_structure = self.extract_document_structure(content, doc_id)
        
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

# --- Collection Management Actions ---
def delete_collection(display_name: str):
    """Deletes a ChromaDB collection by display name."""
    # Convert display name to actual collection name
    actual_collection_name = COLLECTION_MAPPING.get(display_name, display_name)
    
    try:
        chroma_client = get_chroma_client()
        chroma_client.delete_collection(name=actual_collection_name)
        print(f"Successfully deleted collection '{actual_collection_name}' (display name: '{display_name}').")
    except chromadb.errors.NotFoundError:
        print(f"Collection '{actual_collection_name}' not found. No action needed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e

def index_miriad_dataset(chroma_client):
    """Indexes the Miriad dataset into a ChromaDB collection."""
    collection_name = "miriad_knowledge"
    SAFE_PAYLOAD_LIMIT_BYTES = 500000
    MAX_DOCS_PER_BATCH = 16

    # Delete existing collection if it exists
    try:
        existing_collection = chroma_client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists. Deleting and recreating...")
        chroma_client.delete_collection(name=collection_name)
    except chromadb.errors.NotFoundError:
        print(f"Collection '{collection_name}' not found. Creating new collection...")

    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    )

    print("Loading Miriad dataset...")
    try:
        dataset = load_dataset("miriad/miriad-5.8M", split="train[:20000]")
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        raise e

    total_docs = len(dataset)
    current_batch_docs = []
    current_batch_ids = []
    current_payload_size = 0
    document_counter = 0

    for i, row in enumerate(dataset):
        document = f"Question: {row['question']}\nAnswer: {row['answer']}"
        doc_id = f"miriad_{i}"
        doc_size = len(json.dumps(document))

        if (current_payload_size + doc_size > SAFE_PAYLOAD_LIMIT_BYTES) or (len(current_batch_docs) >= MAX_DOCS_PER_BATCH):
            if current_batch_docs:
                try:
                    embeddings = tei_embedding_function(current_batch_docs)
                    collection.add(
                        documents=current_batch_docs,
                        embeddings=embeddings,
                        ids=current_batch_ids
                    )
                    print(f"Ingested {document_counter} / {total_docs} documents.")
                except requests.exceptions.HTTPError as e:
                    print(f"Error getting embeddings from TEI: {e}")
                    raise e

            current_batch_docs = [document]
            current_batch_ids = [doc_id]
            current_payload_size = doc_size
        else:
            current_batch_docs.append(document)
            current_batch_ids.append(doc_id)
            current_payload_size += doc_size

        document_counter += 1

    if current_batch_docs:
        try:
            embeddings = tei_embedding_function(current_batch_docs)
            collection.add(
                documents=current_batch_docs,
                embeddings=embeddings,
                ids=current_batch_ids
            )
            print(f"Ingested {document_counter} / {total_docs} documents.")
        except requests.exceptions.HTTPError as e:
            print(f"Error getting embeddings from TEI (final batch): {e}")
            raise e

    print("\nIndexing complete! The 'miriad_knowledge' collection is ready to use.")

def index_nice_knowledge(chroma_client):
    """Indexes the NICE knowledge into a ChromaDB collection."""
    processor = DocumentProcessor(chroma_client)
    collection_name = "nice_knowledge"
    
    # Delete existing collection if it exists
    try:
        existing_collection = chroma_client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists. Deleting and recreating...")
        chroma_client.delete_collection(name=collection_name)
    except chromadb.errors.NotFoundError:
        print(f"Collection '{collection_name}' not found. Creating new collection...")
    
    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=None
    )

    doc_links = fetch_nice_guidance_index() 
    if not doc_links:
        print("No documents found.")
        raise Exception("Failed to fetch NICE guidance documents")
    
    total_chunks = 0
    for i, doc in enumerate(doc_links):
        print(f"Document {i+1}/{len(doc_links)}: {doc['guidance_number']}")
        
        chunks = processor.process_document(
            doc['uri'], 
            doc['guidance_number'], 
            doc['guidance_number']
        )
        
        if chunks:
            texts = [chunk["text"] for chunk in chunks]
            ids = [chunk["id"] for chunk in chunks]
            metadata = [{"type": chunk.get("type", "unknown"), 
                        "doc_id": doc['guidance_number']} for chunk in chunks]
            
            try:
                embeddings = tei_embedding_function(texts)
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
                # Continue with next document instead of failing completely
                continue
    
    if total_chunks == 0:
        raise Exception("No chunks were successfully indexed")
    
    print(f"Indexing complete! {total_chunks} chunks in collection.")


# --- Command Line Interface ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python manage_collections.py <action> <collection_name>")
        print("Actions: delete, index")
        print("Collection names: 'Miriad Knowledge', 'Nice Knowledge', 'My Documents'")
        sys.exit(1)

    action = sys.argv[1].lower()
    collection_display_name = sys.argv[2]
    
    client = get_chroma_client()

    try:
        if action == "delete":
            delete_collection(collection_display_name)
        elif action == "index":
            # Map display name to actual collection for indexing
            actual_collection_name = COLLECTION_MAPPING.get(collection_display_name, collection_display_name)
            
            if collection_display_name == "Miriad Knowledge":
                index_miriad_dataset(client)
            elif collection_display_name == "Nice Knowledge":
                index_nice_knowledge(client)
            else:
                print(f"Error: Indexing for '{collection_display_name}' is not supported.")
                print("Only 'Miriad Knowledge' and 'Nice Knowledge' can be indexed.")
                sys.exit(1)
        else:
            print(f"Error: Unknown action '{action}'. Use 'delete' or 'index'.")
            sys.exit(1)
            
        print(f"Action '{action}' completed successfully for '{collection_display_name}'.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)