import os
from dotenv import load_dotenv
from langchain_postgres import PGVectorStore


load_dotenv()
# Retrieve DB credentials from environment variables
DB_USER = os.getenv("POSTGRES_USER", "postgres") # Default user for pgvector/pgvector
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = "pgvector_db" # Service name in docker-compose
DB_PORT = os.getenv("PGVECTOR_PORT_INTERNAL", "5432") # Use internal port 5432 always
DB_NAME = os.getenv("POSTGRES_DB", "postgres") # Default DB for pgvector/pgvector


def setup_vector_store(embeddings):
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    store = PGVector(
        collection_name="documents",
        connection=connection_string,
        embeddings=embeddings,
    )

    return store