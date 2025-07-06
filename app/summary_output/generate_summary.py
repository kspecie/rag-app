import os
from dotenv import load_dotenv
import requests
from app.embed_and_store.store import setup_vector_store
from app.embed_and_store.embed import get_tei_instance
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain.schema import Document
from typing import List

load_dotenv()


SUMMARY_TEMPLATE = """
You are a clinical note assistant. Based on the doctor-patient transcript below, generate a summary using this template:

## Summary of Doctor-Patient Conversation

- Chief Complaint:
- Medical History:
- Symptoms:
- Doctor's Assessment:
- Recommended Plan:

Transcript:
{transcript}

Context:
{context}
"""

def get_vectorstore(embedding_endpoint: str):
    """Create and return a vectorstore instance."""
    embeddings = get_tei_instance(model=EMBEDDING_ENDPOINT)
    vectorstore = setup_vector_store(embeddings)
    return vectorstore

def get_context(vectorstore, query: str, k: int = 4) -> str:
    """
    Run similarity search on the vectorstore and return combined context.
    """
    similar_docs: List[Document] = vectorstore.similarity_search(query, k=k)
    context = "\n\n".join(doc.page_content for doc in similar_docs)
    return context

def generate_summary(tgi_endpoint: str, prompt: str) -> str:
    """
    Call the TGI service to generate summary text from the prompt.
    """
    response = requests.post(
        tgi_endpoint,
        json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.5,
            }
        }
    )
    if response.status_code != 200:
        raise RuntimeError(f"TGI request failed: {response.status_code} - {response.text}")

    return response.json().get("generated_text", "").strip()

def create_summary(transcript: str, vectorstore, tgi_endpoint: str) -> str:
    """
    High-level function to create summary given transcript,
    embedding vectorstore and TGI endpoint.
    """
    context = get_context(vectorstore, transcript)
    prompt = SUMMARY_TEMPLATE.format(transcript=transcript, context=context)
    summary = generate_summary(tgi_endpoint, prompt)
    return summary

if __name__ == "__main__":
    # Load endpoints from environment
    EMBEDDING_ENDPOINT = os.getenv("TEI_API_URL")  # Your embedding service URL
    TGI_ENDPOINT = os.getenv("TGI_API_URL")        # Your generation service URL

    # Setup once
    vectorstore = get_vectorstore(EMBEDDING_ENDPOINT)

    fake_transcript = """
    Doctor: Hello, what brings you in today?
    Patient: I've had a sore throat and a mild fever for three days.
    Doctor: Any trouble breathing or swallowing?
    Patient: A little trouble swallowing, but no issues breathing.
    Doctor: Okay, let me take a look at your throat...
    """

    summary = create_summary(fake_transcript, vectorstore, TGI_ENDPOINT)
    print("\n=== Generated Summary ===\n")
    print(summary)
