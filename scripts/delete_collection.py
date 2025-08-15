# import os
# import chromadb


# CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
# CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
# # COLLECTION_NAME = "miriad_knowledge"
# # COLLECTION_NAME = "nice_knowledge"
# COLLECTION_NAME = "nice_knowledge_hierarchical"

# try:
#     chroma_client = chromadb.HttpClient(
#         host=CHROMA_HOST, 
#         port=CHROMA_PORT
#     )
#     print(f"Connected to ChromaDB at http://{CHROMA_HOST}:{CHROMA_PORT}")
    
#     # Delete the collection
#     chroma_client.delete_collection(name=COLLECTION_NAME)
    
#     print(f"\nSuccessfully deleted collection '{COLLECTION_NAME}'.")

# except chromadb.errors.NotFoundError:
#     print(f"Error: Collection '{COLLECTION_NAME}' not found. No action needed.")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")


import os
import sys
import chromadb

CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb_service")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")


def delete_collection(collection_name: str):
    """
    Deletes a ChromaDB collection by name.

    Args:
        collection_name (str): The name of the collection to delete.
    """
    try:
        chroma_client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT
        )
        print(f"Connected to ChromaDB at http://{CHROMA_HOST}:{CHROMA_PORT}")

        chroma_client.delete_collection(name=collection_name)
        print(f"\nSuccessfully deleted collection '{collection_name}'.")

    except chromadb.errors.NotFoundError:
        print(f"Error: Collection '{collection_name}' not found. No action needed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_collection.py <collection_name>")
        sys.exit(1)

    collection_to_delete = sys.argv[1]
    delete_collection(collection_to_delete)
