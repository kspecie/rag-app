# app/consumers/rabbitmq_consumer.py
import os
import sys
sys.path.append('/rag-app')  # Add the app root to Python path

from dotenv import load_dotenv
from typing import Dict, Any, Optional
import pika
import json
import time
import requests
from urllib.parse import urlparse
import io

load_dotenv()

# Import libraries for document parsing
import PyPDF2 

# Import retrieval and generation function
from app.core.pipeline import run_retrieval_and_generation_pipeline

# --- Configuration (from environment variables) ---
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq_service")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_INPUT_QUEUE = os.getenv("RABBITMQ_INPUT_QUEUE", "rag_prompt")
RABBITMQ_OUTPUT_QUEUE = os.getenv("RABBITMQ_OUTPUT_QUEUE", "inference_results")

# --- Helper functions for content extraction ---
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from PDF bytes."""
    text = ""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            # PyPDF2's extract_text can return None for empty pages
            text += page.extract_text() if page.extract_text() is not None else ""
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        text = "" # Ensure empty string on error
    return text

def fetch_and_extract_text_from_url(file_url: str, conversation_id: str) -> Optional[str]:
    """
    Fetches content from the provided URL and extracts text based on file type.
    Supports .txt and .pdf.
    """
    if not file_url:
        print(f"[{conversation_id}] No file_url provided.")
        return None

    try:
        print(f"[{conversation_id}] Attempting to fetch content from: {file_url}")
        response = requests.get(file_url, timeout=15) # Increased timeout for potentially larger files
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        parsed_url = urlparse(file_url)
        path = parsed_url.path
        file_extension = os.path.splitext(path)[1].lower()

        extracted_text = None

        if file_extension == '.txt':
            extracted_text = response.text
            print(f"[{conversation_id}] Successfully fetched and extracted text from .txt file.")
        elif file_extension == '.pdf':
            extracted_text = extract_text_from_pdf(response.content)
            if extracted_text:
                print(f"[{conversation_id}] Successfully extracted text from .pdf file.")
            else:
                print(f"[{conversation_id}] Failed to extract meaningful text from .pdf.")
        else:
            print(f"[{conversation_id}] Unsupported file type via URL: {file_extension}. Treating as plain text (may fail for binary).")
            # Fallback for unknown types or if we receive non-PDF/TXT
            # This might lead to garbled text for binary files, but handles general web pages.
            extracted_text = response.text

        return extracted_text

    except requests.exceptions.RequestException as e:
        print(f"[{conversation_id}] Network or HTTP error fetching content from {file_url}: {e}")
        return None
    except Exception as e:
        print(f"[{conversation_id}] An unexpected error occurred while extracting from URL {file_url}: {e}")
        return None


def process_rag_request(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    This function receives the input message from RabbitMQ,
    extracts the transcription (from file_url), runs the RAG pipeline,
    and returns a formatted message for the output queue.
    """
    conversation_id = msg.get("conversation_id", "unknown_id")
    rag_output_summary = ""
    transcribed_content = "" # This will hold the text for your RAG pipeline

    file_url = msg.get("file_url")
    user_prompts = [] # To capture any user prompt in the 'input' array if needed

    # Prioritize transcription from file_url
    if file_url:
        transcribed_content = fetch_and_extract_text_from_url(file_url, conversation_id)
        if transcribed_content:
            print(f"[{conversation_id}] Using transcribed content from file_url (excerpt: {transcribed_content[:200]}...).")
        else:
            print(f"[{conversation_id}] Could not fetch/extract text from file_url. Checking 'input' array as fallback.")

    # As a fallback, or if 'input' contains a different kind of prompt
    # The rag_prompt example had: input: [ { "role": "user", "content": "prompt" } ]
    # If this 'prompt' is *also* part of the conversation or a standalone input, handle it.
    # For now, let's assume if file_url doesn't yield content, this is the main input.
    if not transcribed_content and "input" in msg and isinstance(msg["input"], list):
        for item in msg["input"]:
            if isinstance(item, dict) and item.get("role") == "user" and "content" in item:
                user_prompts.append(item["content"])
        transcribed_content = " ".join(user_prompts) if user_prompts else ""
        if transcribed_content:
            print(f"[{conversation_id}] Using transcribed content from 'input' array (excerpt: {transcribed_content[:200]}...).")
        else:
            print(f"[{conversation_id}] No 'content' found in 'input' array.")


    if not transcribed_content:
        rag_output_summary = "Error: No transcription content found from file_url or input array."
        print(f"[{conversation_id}] Error: {rag_output_summary}")
    else:
        try:
            # Call run_retrieval_and_generation_pipeline function
            # It expects a string for 'transcribed_conversation'
            summary = run_retrieval_and_generation_pipeline(
                transcribed_conversation=transcribed_content
            )

            if summary:
                rag_output_summary = summary
                print(f"[{conversation_id}] RAG summary generated successfully.")
            else:
                rag_output_summary = "Failed to generate summary from pipeline (returned None or empty)."
                print(f"[{conversation_id}] Error: Pipeline returned no summary.")

        except Exception as e:
            rag_output_summary = f"Error during RAG processing: {e}"
            print(f"[{conversation_id}] Error during RAG processing: {e}")

    # Construct the output message as per the 'inference_result' structure
    output_message = {
        "conversation_id": conversation_id,
        "result": rag_output_summary
    }
    return output_message

def wait_for_services():
    """Wait for dependent services to be ready"""
    print("Waiting for dependent services to be ready...")
    
    # Add any service health checks here if needed
    # For example, you might want to check if ChromaDB is ready
    time.sleep(10)  # Simple wait, you could make this more sophisticated
    
    print("Services should be ready now.")

def main():
    print("Starting RAG RabbitMQ Consumer...")
    
    # Wait for dependent services
    wait_for_services()
    
    connection = None # Initialize connection to None
    max_retries = 30  # Number of times to try connecting
    retry_delay = 5   # Seconds to wait between retries

    # --- RabbitMQ Connection Retry Loop ---
    for i in range(max_retries):
        try:
            print(f"Attempting to connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT} (Attempt {i+1}/{max_retries})...")
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials,
                    heartbeat=120 # Recommended for long-lived connections
                )
            )
            print("Successfully connected to RabbitMQ!")
            break # Exit loop if connection is successful
        except pika.exceptions.AMQPConnectionError as e:
            print(f"RabbitMQ connection failed: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"An unexpected error occurred during RabbitMQ connection: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    if not connection:
        print(f"Failed to connect to RabbitMQ after {max_retries} attempts. Exiting.")
        return

    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_INPUT_QUEUE, durable=True)
    channel.queue_declare(queue=RABBITMQ_OUTPUT_QUEUE, durable=True)

    def on_message(ch, method, properties, body):
        try:
            msg = json.loads(body)
            print(f"Received message: {msg}")

            # Check for essential keys: conversation_id and either file_url or input
            if "conversation_id" not in msg or ("file_url" not in msg and "input" not in msg):
                print(f"Received message missing 'conversation_id' or both 'file_url'/'input' keys. Skipping: {msg}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            updated_msg = process_rag_request(msg)

            # Send the *newly constructed* updated_msg to the output queue
            channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_OUTPUT_QUEUE,
                body=json.dumps(updated_msg),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE # Make messages persistent
                )
            )
            print(f"Processed and published for conversation_id={msg.get('conversation_id')} to {RABBITMQ_OUTPUT_QUEUE}.")
        except json.JSONDecodeError:
            print(f"Failed to decode message body as JSON: {body.decode()}")
        except Exception as e:
            print(f"Error processing message for delivery_tag {method.delivery_tag}: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    # Set QoS to process one message at a time
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(
        queue=RABBITMQ_INPUT_QUEUE,
        on_message_callback=on_message,
        auto_ack=False # Explicitly acknowledge messages
    )
    
    print(f"RAG service listening for messages on {RABBITMQ_INPUT_QUEUE}...")
    print("To exit press CTRL+C")
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Received interrupt signal. Stopping consumer...")
        channel.stop_consuming()
        connection.close()
        print("Consumer stopped.")

if __name__ == '__main__':
    main()