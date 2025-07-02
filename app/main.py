from data_preparation import load_and_chunk
from vector_store import embed_and_store


def main():
    chunks = load_and_chunk("convo1.txt")
    
if __name__ == "__main__":
    # chunks = load_and_chunk("convo1.txt")
    # print(f"Loaded {len(chunks)} chunks")
    # print(chunks[0]) #print first chunk and metadata
    embed_and_store("convo1.txt")
    
#this is just a test.
