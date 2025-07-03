
import os
from dotenv import load_dotenv
from data_preparation import load_and_chunk
from langchain_community.vectorstores.pgvector import PGVector
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain.docstore.document import Document

load_dotenv()

def setup_vector_store():
    embeddings = HuggingFaceEndpointEmbeddings(
        model="http://tei_service:80",
        huggingfacehub_api_token=os.getenv("HF_TOKEN","")
    )

    # Retrieve DB credentials from environment variables
    DB_USER = os.getenv("POSTGRES_USER", "postgres") # Default user for pgvector/pgvector
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = "pgvector_db" # Service name in docker-compose
    DB_PORT = os.getenv("PGVECTOR_PORT_INTERNAL", "5432") # Use internal port 5432 always
    DB_NAME = os.getenv("POSTGRES_DB", "postgres") # Default DB for pgvector/pgvector

    if not DB_PASSWORD:
        raise ValueError("POSTGRES_PASSWORD environment variable not set.")

    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print(f"Connecting to PGVector with connection string: {connection_string.split('@')[0]}@...:{DB_PORT}/{DB_NAME}") # Print obscured password

    store = PGVector(
        collection_name="documents",
        connection_string=connection_string,
        embedding_function=embeddings,
        pre_delete_collection=False
    )

    return store


def embed_and_store(file_path):
    chunks = load_and_chunk(file_path)

    #convert strings to documents
    docs = [Document(page_content=chunk)for chunk in chunks]
    store = setup_vector_store()
    store.add_documents(docs)

