# app/main.py
import os
from dotenv import load_dotenv # Keep this for loading .env vars in main
from vector_store import embed_and_store
from rag_pipeline import get_summarization_chain # Import the new function

# Load environment variables from .env file
load_dotenv()

# Define constants
CONVO_FILE_PATH = "/rag_app/data/raw_data/convo1.txt"

def main():
    print(f"Attempting to load and process file from: {CONVO_FILE_PATH}")
    
    # 1. Embed and store the conversation (only runs if needed, based on pre_delete_collection)
    embed_and_store(CONVO_FILE_PATH)
    print("Conversation embedded and stored successfully (if not already present).")

    # 2. Load the full conversation text for summarization
    try:
        with open(CONVO_FILE_PATH, 'r') as f:
            full_conversation_text = f.read()
    except FileNotFoundError:
        print(f"Error: Conversation file not found at {CONVO_FILE_PATH}")
        return

    # Define the summarization template here, as it's needed for the invoke call
    summary_template = """Patient Name:
Date of Visit:
Chief Complaint:
Vital Signs:
Patient History (new symptoms/concerns):
Doctor's Assessment/Findings:
Treatment Plan/Recommendations:
Follow-up Schedule:"""

    # 3. Get the summarization chain from rag_pipeline.py
    summarization_chain = get_summarization_chain()

    print("\nGenerating summary with Med42. This may take a moment...")
    try:
        # 4. Invoke the summarization chain
        generated_summary = summarization_chain.invoke({
            "conversation": full_conversation_text,
            "template": summary_template # Pass the template directly here
        })
        
        print("\n--- Generated Summary ---")
        print(generated_summary)
        print("-------------------------")

    except Exception as e:
        print(f"Error generating summary: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging

if __name__ == "__main__":
   main()
