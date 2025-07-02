import os

def load_and_chunk(filename):
    raw_folder = "./data/raw_data"
    file_path = os.path.join(raw_folder, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    print(raw_text[:500])

    chunks = raw_text.split("\n\n") #split by paragraph

    chunk_data = []

    for i, chunk in enumerate(chunks):
        metadata = {
            "source_file": filename,
            "chunk_index": i,
            "chunk_length": len(chunk)
        }
        chunk_data.append({
            "text": chunk,
            "metadata": metadata
        })
    return chunk_data