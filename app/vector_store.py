from data_preparation import load_and_chunk
from langchain_community.vectorstores.pgvector import PGVector
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain.docstore.document import Document

def setup_vector_store():
    embeddings = HuggingFaceEndpointEmbeddings(
        model="http://localhost:9002",
        huggingfacehub_api_token=""
    )

    store = PGVector(
        collection_name="documents",
        connection_string="postgresql+psycopg2://postgres:postgres@localhost:9003/postgres",
        embedding_function=embeddings,
        pre_delete_collection=True
    )

    return store


def embed_and_store(file_path):
    chunks = load_and_chunk(file_path)

    #convert strings to documents
    docs = [Document(page_content=chunk)for chunk in chunks]
    store = setup_vector_store()
    store.add_documents(docs)

