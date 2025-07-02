import os
from vector_store import embed_and_store


def main():
    CONVO_FILE_PATH = "/rag_app/data/raw_data/convo1.txt"
    embed_and_store(CONVO_FILE_PATH)
    
if __name__ == "__main__":
   main()
    
