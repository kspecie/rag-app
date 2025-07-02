# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Hello, world!"}


from data_preparation import load_and_chunk

if __name__ == "__main__":
    chunks = load_and_chunk("convo1.txt")
    print(f"Loaded {len(chunks)} chunks")
    print(chunks[0]) #print first chunk and metadata