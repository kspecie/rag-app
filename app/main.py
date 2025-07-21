import os
import sys
import pysqlite3
from dotenv import load_dotenv

# workaround for chromadb/sqlite3 before anything else that might import it
sys.modules["sqlite3"] = pysqlite3
sys.modules["_sqlite3"] = pysqlite3.dbapi2

load_dotenv()

from app.data_ingestion.document_loader import load_documents
from app.data_ingestion.split_and_chunk import split_documents_into_chunks
from app.embed_and_store.embed import create_embeddings
from app.embed_and_store.store import store_chunks_in_chroma
from app.retrieval.retrieve import retrieve_relevant_chunks
from app.generation.generate_summary import generate_summary

def run_ingestion_pipeline(raw_data_dir: str):
    """
    Runs the document ingestion pipeline: loads, splits, and chunks documents.
    """
    print("\n--- Starting Document Ingestion Pipeline ---")

    # 1. Load Documents
    print("Step 1: Loading documents...")
    documents = load_documents(raw_data_dir)
    if not documents:
        print("No documents loaded. Exiting ingestion pipeline.")
        return [] # Return an empty list if no docs

    # 2. Split and Chunk Documents
    print("Step 2: Splitting documents into chunks...")
    chunks = split_documents_into_chunks(documents)
    if not chunks:
        print("No chunks generated. Exiting ingestion pipeline.")
        return []

    print(f"Ingestion pipeline complete. Generated {len(chunks)} chunks.")
    return chunks

def run_embedding_and_storage_pipeline(chunks: list):
    """
    Generates embeddings for chunks and stores them in the vector database.
    """
    print("\n--- Starting Embedding and Storage Pipeline ---")

    # 3. Create Embeddings
    print("Step 3: Generating embeddings for chunks...")
    #call tei_service
    embedded_chunks = create_embeddings(chunks, os.getenv("TEI_SERVICE_URL"))
    if not embedded_chunks:
        print("No embeddings generated. Exiting embedding pipeline.")
        return

    # 4. Store Embeddings in Vector DB
    print("Step 4: Storing embeddings and chunks in ChromaDB...")
    #call chromadb
    store_chunks_in_chroma(embedded_chunks, os.getenv("CHROMADB_SERVICE_URL"), os.getenv("CHROMA_COLLECTION_NAME"))
    print("Embedding and Storage pipeline complete.")


def run_retrieval_and_generation_pipeline(transcribed_conversation: str):
    """
    Runs the retrieval and generation pipeline: retrieves relevant chunks and generates a summary.
    """
    print("\n--- Starting Retrieval and Generation Pipeline ---")

    # 5. Retrieve Relevant Chunks
    print(f"Step 5: Retrieving relevant chunks for query: '{transcribed_conversation}'")
    relevant_chunks = retrieve_relevant_chunks(transcribed_conversation, os.getenv("CHROMADB_SERVICE_URL"), os.getenv("CHROMA_COLLECTION_NAME"))
    if not relevant_chunks:
        print("No relevant chunks found. Cannot generate summary.")
        return None

    print(f"Found {len(relevant_chunks)} relevant chunks.")

    # 6. Generate Summary
    print("Step 6: Generating summary...")
    #call tgi_service
    #pass query and retrieved content to the LLM
    summary = generate_summary(transcribed_conversation, relevant_chunks, os.getenv("TGI_SERVICE_URL"))
    if not summary:
        print("Failed to generate summary.")
        return None

    print("\n--- Generated Summary ---")
    print(summary)
    print("--- End Summary ---")
    print("Retrieval and Generation pipeline complete.")
    return summary


def main():
    """
    Main function to orchestrate the RAG application.
    """
    load_dotenv()

    RAW_DATA_DIRECTORY = os.getenv("RAW_DATA_DIRECTORY", "/rag_app/data/raw_data")

    # --- Ingestion Pipeline ---
    processed_chunks = run_ingestion_pipeline(RAW_DATA_DIRECTORY)

    if processed_chunks:
        # --- Embedding and Storage Pipeline ---
        run_embedding_and_storage_pipeline(processed_chunks)

        print("\n--- All data indexed. Ready for Retrieval and Generation ---")

        # --- Retrieval and Generation Pipeline ---
        # current - hardcode a sample convo

        sample_conversation = """Nurse Sarah: "Alright, Mr. Harrison, just a few more checks here. Blood pressure looks good, 120 over 80. And your pulse is a steady 72. How have you been feeling generally?"
Mr. Harrison: "Pretty good, Nurse. Just a bit tired sometimes, and I've had this nagging little cough on and off for a few weeks."
Nurse Sarah: "Okay, thanks for letting me know. I'll make a note of that for Dr. Evans. Your temperature is normal, 37 degrees Celsius. And your weight is 85 kilograms, which is consistent with last year. Dr. Evans will be with you shortly."
Dr. Evans: "Good morning, Mr. Harrison! Thanks for coming in for your annual check-up. Nurse Sarah tells me you've been feeling a bit tired and have a cough?"
Mr. Harrison: "Good morning, Dr. Evans. Yes, that's right. The tiredness isn't constant, but I've noticed it more in the afternoons, even if I've had a good night's sleep. And the cough, it's dry, and usually just a few coughs here and there, but it can be annoying, especially at night sometimes."
Dr. Evans: "I see. Let's explore that a bit more. When did the tiredness start to become noticeable? And for the cough, have you had any fevers, chills, or shortness of breath with it? Any chest pain?"
Mr. Harrison: "The tiredness, probably the last two or three months, maybe a bit longer. And no, thankfully, no fevers or chills with the cough, and I'm not short of breath. No chest pain either, just the dry cough."
Dr. Evans: "That's good to hear. And anything else bothering you? Any other minor concerns we should discuss today?"
Mr. Harrison: "Well, since you ask, I've also had a few episodes of heartburn lately. Nothing severe, but it flares up after certain meals, especially if I eat late."
Dr. Evans: "Thanks for sharing that, Mr. Harrison. It's helpful to get a full picture. For the heartburn, are there any specific foods that trigger it? And how often would you say these episodes occur?"
Mr. Harrison: "Mostly spicy food, or really rich, fatty meals. And it's probably about once or twice a week, sometimes more if I'm not careful with what I eat. High cholestrol also runs in my family."
Dr. Evans: "Understood. Okay, let's do a thorough physical examination first. I'll listen to your heart and lungs, check your throat, and feel your abdomen. Nurse Sarah, could you hand me the stethoscope, please?"
Nurse Sarah: "Of course, Doctor." (Hands the stethoscope to Dr. Evans.)
(Dr. Evans performs the examination.)
Dr. Evans: "Alright, everything sounds clear in your lungs, and your heart rhythm is regular. Your throat looks fine too. Based on what you've described, the tiredness and dry cough could be due to a few things, including post-nasal drip or even just the seasonal changes we've had recently. For the heartburn, we can look at some dietary adjustments and potentially some over-the-counter remedies first. We might also consider some blood tests just to rule out any underlying causes for the fatigue, and perhaps a chest X-ray if the cough persists. How many times a week do you drink?"
Mr. Harrison: "About two drinks per week.  Everything else sounds reasonable, Doctor."
Dr. Evans: "Great. Nurse Sarah will give you some information on managing heartburn with diet, and we'll schedule those blood tests for you. She'll also explain how to collect a sputum sample for the cough, just in case, though I don't anticipate anything serious."
Nurse Sarah: "Absolutely, Mr. Harrison. I have a few pamphlets here on dietary changes for heartburn, and I can book your blood test appointment for next week. I'll also go over the instructions for the sputum sample with you before you leave."
Dr. Evans: "Perfect. Mr. Harrison, we'll review all the results once they come in, and then we can discuss the next steps. Does that sound good to you?"
Mr. Harrison: "Yes, Dr. Evans, that sounds very thorough. Thank you both."
"""     
        print("\n--- Processing new transcribed conversation ---")
        _ = run_retrieval_and_generation_pipeline(sample_conversation) 

    else:
        print("No chunks to process. RAG pipeline halted.")

if __name__ == "__main__":
    main()