from typing import List, Dict, Any, Optional
import pika
import json
import os
import time

# Import the core RAG pipeline function
from app.core.pipeline import run_retrieval_and_generation_pipeline

# --- Configuration (from environment variables) ---
# It's best practice to get these from environment variables in a Docker setup
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq_service") 
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_INPUT_QUEUE = os.getenv("RABBITMQ_INPUT_QUEUE", "rag_prompt")
RABBITMQ_OUTPUT_QUEUE = os.getenv("RABBITMQ_OUTPUT_QUEUE", "inference_results")


def process_rag_request(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    This function receives the input message from RabbitMQ,
    runs the RAG pipeline using existing core logic,
    and returns a modified message for the output queue.
    """
    conversation_id = msg.get("conversation_id", "unknown_id") # Expecting a conversation_id
    transcribed_conversation = msg.get("transcription", "") # Expecting the full transcription

    print(f"[{conversation_id}] Received message for RAG processing.")
    print(f"[{conversation_id}] Transcribed Conversation (excerpt): {transcribed_conversation[:200]}...")

    if not transcribed_conversation:
        msg["status"] = "failed"
        msg["error"] = "No 'transcription' found in input message."
        msg["rag_output_summary"] = "Error: No transcription provided."
        print(f"[{conversation_id}] Error: No transcription provided in message.")
        return msg

    try:
        # Call your existing run_retrieval_and_generation_pipeline function
        summary = run_retrieval_and_generation_pipeline(
            transcribed_conversation=transcribed_conversation
        )

        if summary:
            msg["status"] = "success"
            msg["rag_output_summary"] = summary
            print(f"[{conversation_id}] RAG summary generated successfully.")
        else:
            msg["status"] = "failed"
            msg["error"] = "Summary generation returned None."
            msg["rag_output_summary"] = "Error generating summary: Pipeline returned no summary."
            print(f"[{conversation_id}] Error: Pipeline returned no summary.")

    except Exception as e:
        msg["status"] = "failed"
        msg["error"] = str(e)
        msg["rag_output_summary"] = f"Error generating summary: {e}"
        print(f"[{conversation_id}] Error during RAG processing: {e}")

    return msg

def main():
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
                    heartbeat=60 # Recommended for long-lived connections
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
        # If connection fails after all retries, you might want to exit the application
        # or raise an error to indicate a critical failure.
        # For a Docker container, exiting here will cause it to restart (if restart policy is set).
        return 
    # --- End RabbitMQ Connection Retry Loop ---

    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_INPUT_QUEUE, durable=True)
    channel.queue_declare(queue=RABBITMQ_OUTPUT_QUEUE, durable=True)

    def on_message(ch, method, properties, body):
        try:
            msg = json.loads(body)
            # Add a safety check for the expected 'transcription' key
            if "transcription" not in msg:
                print(f"Received message without 'transcription' key. Skipping: {msg}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            updated_msg = process_rag_request(msg)

            # Send updated message to output queue
            channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_OUTPUT_QUEUE,
                body=json.dumps(updated_msg),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE # Make messages persistent
                )
            )
            print(f"Processed and published for conversation_id={msg.get('conversation_id')}")
        except json.JSONDecodeError:
            print(f"Failed to decode message body as JSON: {body.decode()}")
        except Exception as e:
            print("Error processing message:", e)
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=RABBITMQ_INPUT_QUEUE,
        on_message_callback=on_message,
        auto_ack=False # Explicitly acknowledge messages
    )
    print(f"RAG service listening for messages on {RABBITMQ_INPUT_QUEUE}...")
    channel.start_consuming()

if __name__ == '__main__':
    main()