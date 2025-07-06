from pathlib import Path
import os
from dotenv import load_dotenv
from typing import List, Optional
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEndpointEmbeddings

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

def get_tei_instance(
    model="http://tei_service:80",
    huggingfacehub_api_token=os.getenv("HF_TOKEN","")
) -> HuggingFaceEndpointEmbeddings: 

    if not huggingfacehub_api_token:
        print("Warning: HF_TOKEN not provided.")
        print(f"Initializing HuggingFaceEndpointEmbeddings with endpoint: {endpoint_url}")

    try:
        embedding_model = HuggingFaceEndpointEmbeddings(
            huggingfacehub_api_token=huggingfacehub_api_token,
            model=model)
        return embedding_model

    except Exception as e:
        print(f"Error initializing HuggingFaceEndpointEmbeddings for TEI service: {e}")
        print("Ensure 'tei_service:80' is accessible and the TEI service is running.")
        raise # Re-raise to signal failure to the caller

def batched_embedding(
    input: List[str],
    model: HuggingFaceEndpointEmbeddings,
    batch_size: int = 8
) -> List[List[float]]:
    """
    Embeds text in batches to avoid exceeding TEI payload limits.

    Args:
        texts (List[str]): List of text chunks to embed.
        model (HuggingFaceEndpointEmbeddings): The initialized embedding model.
        batch_size (int): Number of chunks to send per request.

    Returns:
        List[List[float]]: Embeddings for all text chunks.
    """
    all_embeddings = []
    for i in range(0, len(input), batch_size):
        batch = input[i:i + batch_size]
        print(f"[BATCHING] Embedding batch {i//batch_size + 1}: {len(batch)} chunks")
        try:
            embeddings = model.embed_documents(batch)
            all_embeddings.extend(embeddings)
        except Exception as e:
            print(f"Error embedding batch {i//batch_size + 1}: {e}")
            raise
    return all_embeddings


def generate_embeddings(
    document_chunks: List[Document],
    embeddings_model: HuggingFaceEndpointEmbeddings
) -> List[List[float]]:
    """
    Takes a list of LangChain Document objects (chunks) and generates their embeddings.

    Args:
        document_chunks (List[Document]): The list of LangChain Document objects to embed.
        embeddings_model (HuggingFaceEndpointEmbeddings): An initialized LangChain embeddings model.

    Returns:
        List[List[float]]: A list of embedding vectors, where each vector is a list of floats.
                           The order corresponds to the input document_chunks.
    """
    if not document_chunks:
        print("No document chunks provided for embedding. Returning empty list.")
        return []

    if not embeddings_model:
        print("Embeddings model not provided. Cannot generate embeddings. Returning empty list.")
        return []

    print(f"\n--- Generating embeddings for {len(document_chunks)} chunks ---")
    
    # LangChain's embedding models have an embed_documents method
    texts_to_embed = [doc.page_content for doc in document_chunks]
    print(f"Number of chunks: {len(texts_to_embed)}")
    print(f"Total characters across all chunks: {sum(len(t) for t in texts_to_embed)}")
    print(f"First chunk preview: {texts_to_embed[0][:20]}...")

    return batched_embedding(texts_to_embed, embeddings_model)




    