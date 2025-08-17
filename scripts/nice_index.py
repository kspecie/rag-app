import os
import requests
import chromadb
import json
import re
from typing import List, Dict, Any
import hashlib
from chromadb.utils import embedding_functions
import tiktoken

# --- Configuration ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
MAX_CHROMA_BATCH_SIZE = 16

# NICE API config
NICE_API_KEY = os.getenv("NICE_API_KEY", "your_api_key_here") 
NICE_API_BASE_URL = "https://api.nice.org.uk"

# Chunking settings
# Use a reasonable token limit. With k=1, this should fit within the LLM's context window.
MAX_CHUNK_TOKENS = 600
OVERLAP_TOKENS = 50

class DocumentProcessor:
    def __init__(self):
        self.chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        # Using a direct SentenceTransformer model for embedding as per your previous code
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using tiktoken for accuracy."""
        return len(self.tokenizer.encode(text))

    def clean_text(self, text: str) -> str:
        """Applies data cleaning strategies to the text."""
        text = re.sub(r"\[[0-9]+\]", "", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        text = text.lower()
        return text
    
    def create_document_summary(self, content: str, doc_id: str, title: str) -> str:
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        summary_parts = [f"NICE Guidance {doc_id}: {title}"]
        current_tokens = self.estimate_tokens(summary_parts[0])
        
        for para in paragraphs[:5]:
            para_tokens = self.estimate_tokens(para)
            if current_tokens + para_tokens > MAX_CHUNK_TOKENS:
                break
            summary_parts.append(para)
            current_tokens += para_tokens
        
        summary = "\n\n".join(summary_parts)
        
        if self.estimate_tokens(summary) > MAX_CHUNK_TOKENS:
            truncated_summary = self.tokenizer.decode(self.tokenizer.encode(summary)[:MAX_CHUNK_TOKENS])
            summary = truncated_summary + "..."
        
        return summary
    
    def extract_document_structure(self, content: str, doc_id: str) -> Dict[str, Any]:
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

    def create_focused_chunks(self, section: Dict[str, Any], doc_id: str, doc_title: str) -> List[Dict[str, Any]]:
        section_title = section["title"]
        content = section["content"]
        
        context_header_template = f"Document: {doc_title} ({doc_id})\nSection: {section_title}\n\n"
        header_tokens = self.estimate_tokens(context_header_template)
        
        chunks = []
        sentences = re.split(r'(?<=[.?!])\s+', content)
        current_chunk_sentences = []
        chunk_num = 0
        
        for sentence in sentences:
            sentence_tokens = self.estimate_tokens(sentence)
            
            if sentence_tokens + header_tokens > MAX_CHUNK_TOKENS:
                print(f"Warning: A very long sentence was found in {doc_id}. Splitting it.")
                sentence_parts = self._split_long_text(sentence, MAX_CHUNK_TOKENS - header_tokens)
                
                if current_chunk_sentences:
                    chunk_text = " ".join(current_chunk_sentences)
                    full_context_chunk = f"{context_header_template}Part {chunk_num + 1}:\n\n{chunk_text}"
                    chunks.append({
                        "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
                        "text": full_context_chunk,
                        "type": "section_chunk",
                        "section_title": section_title,
                        "part_number": chunk_num
                    })
                    chunk_num += 1
                    current_chunk_sentences = [] 
                
                for part in sentence_parts:
                    full_context_chunk = f"{context_header_template}Part {chunk_num + 1}:\n\n{part}"
                    chunks.append({
                        "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
                        "text": full_context_chunk,
                        "type": "section_chunk",
                        "section_title": section_title,
                        "part_number": chunk_num
                    })
                    chunk_num += 1
                continue
            
            test_chunk_text = " ".join(current_chunk_sentences + [sentence])
            
            if self.estimate_tokens(test_chunk_text) + header_tokens <= MAX_CHUNK_TOKENS - OVERLAP_TOKENS:
                current_chunk_sentences.append(sentence)
            else:
                if current_chunk_sentences:
                    chunk_text = " ".join(current_chunk_sentences)
                    full_context_chunk = f"{context_header_template}Part {chunk_num + 1}:\n\n{chunk_text}"
                    chunks.append({
                        "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
                        "text": full_context_chunk,
                        "type": "section_chunk",
                        "section_title": section_title,
                        "part_number": chunk_num
                    })
                    
                    overlap_sentences = current_chunk_sentences[-2:]
                    current_chunk_sentences = overlap_sentences + [sentence]
                    chunk_num += 1
                else:
                    current_chunk_sentences.append(sentence)
        
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            full_context_chunk = f"{context_header_template}Part {chunk_num + 1}:\n\n{chunk_text}"
            
            chunks.append({
                "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
                "text": full_context_chunk,
                "type": "section_chunk",
                "section_title": section_title,
                "part_number": chunk_num
            })
        
        return chunks

    def _split_long_text(self, text: str, max_tokens: int) -> List[str]:
        tokens = self.tokenizer.encode(text)
        chunks = []
        current_pos = 0
        while current_pos < len(tokens):
            end_pos = min(current_pos + max_tokens, len(tokens))
            chunk_tokens = tokens[current_pos:end_pos]
            chunks.append(self.tokenizer.decode(chunk_tokens))
            current_pos = end_pos
        return chunks
    
    def process_document(self, doc_uri: str, doc_id: str, doc_title: str) -> List[Dict[str, Any]]:
        print(f"  Processing {doc_id}...")
        
        content = self.fetch_full_document_content(doc_uri)
        if not content:
            return []
        
        content = self.clean_text(content)
        
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
        full_doc_url = f"{doc_uri}/full-document" if doc_uri.startswith("http") \
                        else f"{NICE_API_BASE_URL}{doc_uri}/full-document"
        
        headers = {
            "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
            "API-Key": NICE_API_KEY
        }
        
        try:
            response = requests.get(full_doc_url, headers=headers, timeout=30)
            response.raise_for_status()
            full_content_data = response.json()
            content = full_content_data.get('Content', '')
            
            if not content:
                print(f"Warning: No content found for {doc_uri}")
                return ""
            
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {doc_uri}: {e}")
            return ""
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {doc_uri}: {e}")
            return ""

def index_nice_knowledge_hierarchical():
    try:
        processor = DocumentProcessor()
    except Exception as e:
        print(f"Error initializing DocumentProcessor: {e}")
        return

    collection_name = "nice_knowledge_hierarchical"
    
    try:
        processor.chroma_client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists. Skipping indexing.")
        return
    except chromadb.errors.NotFoundError:
        print(f"Collection '{collection_name}' not found. Creating and indexing...")

    collection = processor.chroma_client.create_collection(
        name=collection_name,
        embedding_function=processor.embedding_function
    )
    
    doc_links = fetch_nice_guidance_index() 
    if not doc_links:
        print("No documents found.")
        return
    
    all_chunks_to_add = []
    
    for i, doc in enumerate(doc_links):
        print(f"Document {i+1}/{len(doc_links)}: {doc['guidance_number']}")
        
        try:
            chunks = processor.process_document(
                doc['uri'], 
                doc['guidance_number'], 
                doc['guidance_number']
            )
            all_chunks_to_add.extend(chunks)
        
        except Exception as e:
            print(f"    Error processing {doc['guidance_number']}: {e}")
    
    print(f"\nStarting batch ingestion of {len(all_chunks_to_add)} chunks.")
    
    current_batch_docs = []
    current_batch_ids = []
    current_batch_metadata = []
    total_ingested = 0

    for chunk in all_chunks_to_add:
        current_batch_docs.append(chunk["text"])
        current_batch_ids.append(chunk["id"])
        current_batch_metadata.append({
            "type": chunk.get("type", "unknown"),
            "doc_id": chunk["id"].split('_')[0]
        })

        if len(current_batch_docs) >= MAX_CHROMA_BATCH_SIZE:
            try:
                collection.add(
                    documents=current_batch_docs,
                    ids=current_batch_ids,
                    metadatas=current_batch_metadata
                )
                total_ingested += len(current_batch_docs)
                print(f"Ingested {total_ingested} / {len(all_chunks_to_add)} chunks.")
                
            except Exception as e:
                print(f"Error ingesting batch: {e}")

            current_batch_docs = []
            current_batch_ids = []
            current_batch_metadata = []
            
    if current_batch_docs:
        try:
            collection.add(
                documents=current_batch_docs,
                ids=current_batch_ids,
                metadatas=current_batch_metadata
            )
            total_ingested += len(current_batch_docs)
            print(f"Ingested final batch. Total: {total_ingested} chunks.")
        except Exception as e:
            print(f"Error ingesting final batch: {e}")
            
    print("\nIndexing complete! The 'nice_knowledge_hierarchical' collection is ready to use.")

def fetch_nice_guidance_index():
    print("Fetching NICE guidance index from API...")
    headers = {
        "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
        "API-Key": NICE_API_KEY
    }
    api_url = f"{NICE_API_BASE_URL}/services/guidance/ifp/index"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
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


# import os
# import requests
# import chromadb
# import json
# import re
# from typing import List, Dict, Any
# import hashlib
# from chromadb.utils import embedding_functions
# import tiktoken

# # --- Configuration ---
# CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
# CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
# MAX_CHROMA_BATCH_SIZE = 16

# # NICE API config
# NICE_API_KEY = os.getenv("NICE_API_KEY", "your_api_key_here") 
# NICE_API_BASE_URL = "https://api.nice.org.uk"

# # Chunking settings
# # Adjusted to a balanced value to prevent token errors without losing too much context
# MAX_CHUNK_TOKENS = 400
# OVERLAP_TOKENS = 50

# class DocumentProcessor:
#     def __init__(self):
#         self.chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
#         self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
#         self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
#     def estimate_tokens(self, text: str) -> int:
#         return len(self.tokenizer.encode(text))

#     def clean_text(self, text: str) -> str:
#         """Applies data cleaning strategies to the text."""
#         # Remove common, non-meaningful content
#         text = re.sub(r"\[[0-9]+\]", "", text) # Remove citation numbers like [1], [2]
#         text = re.sub(r"\s+", " ", text) # Replace multiple spaces with a single space
#         text = text.strip() # Remove leading/trailing whitespace
#         text = text.lower() # Convert to lowercase
#         return text

#     def create_document_summary(self, content: str, doc_id: str, title: str) -> str:
#         paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
#         summary_parts = [f"NICE Guidance {doc_id}: {title}"]
#         current_tokens = self.estimate_tokens(summary_parts[0])
        
#         for para in paragraphs[:5]:
#             para_tokens = self.estimate_tokens(para)
#             if current_tokens + para_tokens > MAX_CHUNK_TOKENS:
#                 break
#             summary_parts.append(para)
#             current_tokens += para_tokens
        
#         summary = "\n\n".join(summary_parts)
        
#         if self.estimate_tokens(summary) > MAX_CHUNK_TOKENS:
#             truncated_summary = self.tokenizer.decode(self.tokenizer.encode(summary)[:MAX_CHUNK_TOKENS])
#             summary = truncated_summary + "..."
        
#         return summary
    
#     def extract_document_structure(self, content: str, doc_id: str) -> Dict[str, Any]:
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

#     def create_focused_chunks(self, section: Dict[str, Any], doc_id: str, doc_title: str) -> List[Dict[str, Any]]:
#         section_title = section["title"]
#         content = section["content"]
        
#         context_header_template = f"Document: {doc_title} ({doc_id})\nSection: {section_title}\n\n"
#         header_tokens = self.estimate_tokens(context_header_template)
        
#         chunks = []
#         sentences = re.split(r'(?<=[.?!])\s+', content)
#         current_chunk_sentences = []
#         chunk_num = 0
        
#         for sentence in sentences:
#             sentence_tokens = self.estimate_tokens(sentence)
            
#             if sentence_tokens + header_tokens > MAX_CHUNK_TOKENS:
#                 print(f"Warning: A very long sentence was found in {doc_id}. Splitting it.")
#                 sentence_parts = self._split_long_text(sentence, MAX_CHUNK_TOKENS - header_tokens)
                
#                 if current_chunk_sentences:
#                     chunk_text = " ".join(current_chunk_sentences)
#                     full_context_chunk = f"{context_header_template}Part {chunk_num + 1}:\n\n{chunk_text}"
#                     chunks.append({
#                         "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
#                         "text": full_context_chunk,
#                         "type": "section_chunk",
#                         "section_title": section_title,
#                         "part_number": chunk_num
#                     })
#                     chunk_num += 1
#                     current_chunk_sentences = [] 
                
#                 for part in sentence_parts:
#                     full_context_chunk = f"{context_header_template}Part {chunk_num + 1}:\n\n{part}"
#                     chunks.append({
#                         "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
#                         "text": full_context_chunk,
#                         "type": "section_chunk",
#                         "section_title": section_title,
#                         "part_number": chunk_num
#                     })
#                     chunk_num += 1
#                 continue
            
#             test_chunk_text = " ".join(current_chunk_sentences + [sentence])
            
#             if self.estimate_tokens(test_chunk_text) + header_tokens <= MAX_CHUNK_TOKENS - OVERLAP_TOKENS:
#                 current_chunk_sentences.append(sentence)
#             else:
#                 if current_chunk_sentences:
#                     chunk_text = " ".join(current_chunk_sentences)
#                     full_context_chunk = f"{context_header_template}Part {chunk_num + 1}:\n\n{chunk_text}"
#                     chunks.append({
#                         "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
#                         "text": full_context_chunk,
#                         "type": "section_chunk",
#                         "section_title": section_title,
#                         "part_number": chunk_num
#                     })
                    
#                     overlap_sentences = current_chunk_sentences[-2:]
#                     current_chunk_sentences = overlap_sentences + [sentence]
#                     chunk_num += 1
#                 else:
#                     current_chunk_sentences.append(sentence)
        
#         if current_chunk_sentences:
#             chunk_text = " ".join(current_chunk_sentences)
#             full_context_chunk = f"{context_header_template}Part {chunk_num + 1}:\n\n{chunk_text}"
            
#             chunks.append({
#                 "id": f"{doc_id}_section_{hashlib.md5(section_title.encode()).hexdigest()[:8]}_part_{chunk_num}",
#                 "text": full_context_chunk,
#                 "type": "section_chunk",
#                 "section_title": section_title,
#                 "part_number": chunk_num
#             })
        
#         return chunks

#     def _split_long_text(self, text: str, max_tokens: int) -> List[str]:
#         tokens = self.tokenizer.encode(text)
#         chunks = []
#         current_pos = 0
#         while current_pos < len(tokens):
#             end_pos = min(current_pos + max_tokens, len(tokens))
#             chunk_tokens = tokens[current_pos:end_pos]
#             chunks.append(self.tokenizer.decode(chunk_tokens))
#             current_pos = end_pos
#         return chunks
    
#     def process_document(self, doc_uri: str, doc_id: str, doc_title: str) -> List[Dict[str, Any]]:
#         print(f"  Processing {doc_id}...")
        
#         content = self.fetch_full_document_content(doc_uri)
#         if not content:
#             return []
        
#         # Apply cleaning to the content before further processing
#         content = self.clean_text(content)
        
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
#         full_doc_url = f"{doc_uri}/full-document" if doc_uri.startswith("http") \
#                         else f"{NICE_API_BASE_URL}{doc_uri}/full-document"
        
#         headers = {
#             "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
#             "API-Key": NICE_API_KEY
#         }
        
#         try:
#             response = requests.get(full_doc_url, headers=headers, timeout=30)
#             response.raise_for_status()
#             full_content_data = response.json()
#             content = full_content_data.get('Content', '')
            
#             if not content:
#                 print(f"Warning: No content found for {doc_uri}")
#                 return ""
            
#             content = content.replace('\r\n', '\n').replace('\r', '\n')
#             return content
            
#         except requests.exceptions.RequestException as e:
#             print(f"Error downloading {doc_uri}: {e}")
#             return ""
#         except json.JSONDecodeError as e:
#             print(f"Error parsing JSON from {doc_uri}: {e}")
#             return ""

# def index_nice_knowledge():
#     try:
#         processor = DocumentProcessor()
#     except Exception as e:
#         print(f"Error initializing DocumentProcessor: {e}")
#         return

#     collection_name = "nice_knowledge"
    
#     try:
#         processor.chroma_client.get_collection(name=collection_name)
#         print(f"Collection '{collection_name}' already exists. Skipping indexing.")
#         return
#     except chromadb.errors.NotFoundError:
#         print(f"Collection '{collection_name}' not found. Creating and indexing...")

#     collection = processor.chroma_client.create_collection(
#         name=collection_name,
#         embedding_function=processor.embedding_function
#     )
    
#     doc_links = fetch_nice_guidance_index() 
#     if not doc_links:
#         print("No documents found.")
#         return
    
#     all_chunks_to_add = []
    
#     for i, doc in enumerate(doc_links):
#         print(f"Document {i+1}/{len(doc_links)}: {doc['guidance_number']}")
        
#         try:
#             chunks = processor.process_document(
#                 doc['uri'], 
#                 doc['guidance_number'], 
#                 doc['guidance_number']
#             )
#             all_chunks_to_add.extend(chunks)
        
#         except Exception as e:
#             print(f"    Error processing {doc['guidance_number']}: {e}")
    
#     # Batch the entire list of chunks for ingestion
#     print(f"\nStarting batch ingestion of {len(all_chunks_to_add)} chunks.")
    
#     current_batch_docs = []
#     current_batch_ids = []
#     current_batch_metadata = []
#     total_ingested = 0

#     for chunk in all_chunks_to_add:
#         current_batch_docs.append(chunk["text"])
#         current_batch_ids.append(chunk["id"])
#         current_batch_metadata.append({
#             "type": chunk.get("type", "unknown"),
#             "doc_id": chunk["id"].split('_')[0]
#         })

#         if len(current_batch_docs) >= MAX_CHROMA_BATCH_SIZE:
#             try:
#                 collection.add(
#                     documents=current_batch_docs,
#                     ids=current_batch_ids,
#                     metadatas=current_batch_metadata
#                 )
#                 total_ingested += len(current_batch_docs)
#                 print(f"Ingested {total_ingested} / {len(all_chunks_to_add)} chunks.")
                
#             except Exception as e:
#                 print(f"Error ingesting batch: {e}")

#             # Reset for next batch
#             current_batch_docs = []
#             current_batch_ids = []
#             current_batch_metadata = []
            
#     # Final batch
#     if current_batch_docs:
#         try:
#             collection.add(
#                 documents=current_batch_docs,
#                 ids=current_batch_ids,
#                 metadatas=current_batch_metadata
#             )
#             total_ingested += len(current_batch_docs)
#             print(f"Ingested final batch. Total: {total_ingested} chunks.")
#         except Exception as e:
#             print(f"Error ingesting final batch: {e}")
            
#     print("\nIndexing complete! The 'nice_knowledge' collection is ready to use.")


# def fetch_nice_guidance_index():
#     print("Fetching NICE guidance index from API...")
#     headers = {
#         "Accept": "application/vnd.nice.syndication.guidance+json;version=1.0",
#         "API-Key": NICE_API_KEY
#     }
#     api_url = f"{NICE_API_BASE_URL}/services/guidance/ifp/index"
    
#     try:
#         response = requests.get(api_url, headers=headers, timeout=30)
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

# if __name__ == "__main__":
#     index_nice_knowledge()