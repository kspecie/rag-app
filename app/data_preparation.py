import os
from langchain.text_splitter import TokenTextSplitter
from transformers import GPT2TokenizerFast

def load_and_chunk(filename, chunk_size=300, chunk_overlap=50):
    raw_folder = "/data/raw_data"
    file_path = os.path.join(raw_folder, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    print(raw_text[:500])

    #token based text splitter
    text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    #split into chunks based on tokens
    chunks = text_splitter.split_text(raw_text)
   
    # For debugging: print each chunk with token count
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    for i, chunk in enumerate(chunks):
        token_count = len(tokenizer.encode(chunk))
        print(f"\n--- Chunk {i+1} (Tokens: {token_count}) ---\n{chunk[:300]}...\n")
   
    return chunks