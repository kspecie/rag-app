# # app/main.py
# import os
# from dotenv import load_dotenv # Keep this for loading .env vars in main
# from vector_store import embed_and_store
# from rag_pipeline import get_summarization_chain # Import the new function

# # Load environment variables from .env file
# load_dotenv()

# # Define constants
# CONVO_FILE_PATH = "/rag_app/data/raw_data/convo1.txt"

# def main():
#     print(f"Attempting to load and process file from: {CONVO_FILE_PATH}")
    
#     # 1. Embed and store the conversation (only runs if needed, based on pre_delete_collection)
#     embed_and_store(CONVO_FILE_PATH)
#     print("Conversation embedded and stored successfully (if not already present).")

#     # 2. Load the full conversation text for summarization
#     try:
#         with open(CONVO_FILE_PATH, 'r') as f:
#             full_conversation_text = f.read()
#     except FileNotFoundError:
#         print(f"Error: Conversation file not found at {CONVO_FILE_PATH}")
#         return

#     # Define the summarization template here, as it's needed for the invoke call
#     summary_template = """Patient Name:
# Date of Visit:
# Chief Complaint:
# Vital Signs:
# Patient History (new symptoms/concerns):
# Doctor's Assessment/Findings:
# Treatment Plan/Recommendations:
# Follow-up Schedule:"""

#     # 3. Get the summarization chain from rag_pipeline.py
#     summarization_chain = get_summarization_chain()

#     print("\nGenerating summary with Med42. This may take a moment...")
#     try:
#         # 4. Invoke the summarization chain
#         generated_summary = summarization_chain.invoke({
#             "conversation": full_conversation_text,
#             "template": summary_template # Pass the template directly here
#         })
        
#         print("\n--- Generated Summary ---")
#         print(generated_summary)
#         print("-------------------------")

#     except Exception as e:
#         print(f"Error generating summary: {e}")
#         import traceback
#         traceback.print_exc() # Print full traceback for debugging

# if __name__ == "__main__":
#    main()


# app/main.py
import os
import requests # New import
from dotenv import load_dotenv
from vector_store import embed_and_store # Still needed for ingestion
from rag_pipeline import get_summarization_chain

load_dotenv()

# --- Configuration ---
KNOWLEDGE_BASE_DIR = "/rag_app/data/raw_data"
ALLOWED_EXTENSIONS = ['.txt', '.md']

# The specific conversation file we want to summarize (will be part of context)
CONVO_FILE_TO_SUMMARIZE = "/rag_app/data/raw_data/convo1.txt"

# NEW: Endpoint for the OPEA Retriever Microservice
RETRIEVER_ENDPOINT = "http://retriever:8000/retrieval" # As per OPEA README for pgvector

def get_files_to_ingest(directory):
    files_to_process = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if any(file_path.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                files_to_process.append(file_path)
    return files_to_process

def call_retriever_service(query_text: str, top_k: int = 5) -> str:
    """
    Calls the OPEA Retriever Microservice to get relevant context.
    """
    payload = {
        "text": query_text,
        "size": top_k
    }
    headers = {"Content-Type": "application/json"}

    print(f"Calling Retriever Service at {RETRIEVER_ENDPOINT} with query: '{query_text[:50]}...'")
    try:
        response = requests.post(RETRIEVER_ENDPOINT, json=payload, headers=headers, timeout=60)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        retrieved_data = response.json()

        # The OPEA Retriever typically returns a list of dictionaries with 'text' field
        # e.g., {"retrieved": [{"text": "chunk1", "score": 0.9}, {"text": "chunk2", "score": 0.8}]}
        context_docs = [doc["text"] for doc in retrieved_data.get("retrieved", [])]

        if not context_docs:
            print("Warning: Retriever returned no documents for the query.")
            return "No relevant context found."

        # Join the retrieved chunks into a single string to pass as context
        return "\n\n".join(context_docs)

    except requests.exceptions.ConnectionError as e:
        print(f"Error connecting to Retriever Service at {RETRIEVER_ENDPOINT}: {e}")
        print("Please ensure the 'retriever' Docker container is running and accessible.")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error from Retriever Service: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while calling Retriever Service: {e}")
        raise


def main():
    # --- Data Ingestion Phase (Still crucial to build the KB for Retriever) ---
    print("\n--- Starting Document Ingestion ---")
    files_to_ingest = get_files_to_ingest(KNOWLEDGE_BASE_DIR)

    if not files_to_ingest:
        print(f"No files found in {KNOWLEDGE_BASE_DIR} with extensions: {ALLOWED_EXTENSIONS}")
        print("Please add your knowledge base documents to this directory.")
    else:
        for file_path in files_to_ingest:
            print(f"Embedding and storing: {file_path}")
            embed_and_store(file_path)
        print("--- Document Ingestion Complete ---")

    # --- Summarization Phase (Now leveraging Retriever) ---
    print(f"\n--- Starting Summarization with RAG ---")

    # For summarization, the query sent to the Retriever needs to guide it
    # to pull relevant parts of the conversation (and potentially guidelines).
    # A good query could be a concise prompt related to the summary task.
    # Ensure CONVO_FILE_TO_SUMMARIZE is already ingested into the KB.

    # Example query: You might ask the retriever to find relevant info for a clinical summary.
    # This query will be embedded by TEI and used to search PGVector.
    query_for_retrieval = "Summarize the key medical details, patient history, and treatment plan from a doctor-patient conversation for a clinical report."

    # You can optionally include part of the conversation itself if it's concise enough for an embedding query.
    # If your full conversation is very long, using a general query is better.
    # For simplicity, we'll use a generic query that should hopefully hit chunks of convo1.txt

    try:
        # Call the Retriever Microservice to get relevant context chunks
        retrieved_context = call_retriever_service(query_for_retrieval, top_k=5) # Get top 5 relevant chunks
        print("\n--- Retrieved Context ---")
        print(retrieved_context)
        print("-------------------------")

        if "No relevant context found." in retrieved_context:
            print("Cannot summarize due to lack of relevant context from Retriever.")
            return

        summary_template = """Patient Name: