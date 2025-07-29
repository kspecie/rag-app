# send_message_test.py
import pika
import json
import time
import uuid 

# RabbitMQ details (adjust if running locally without Docker network)
RABBITMQ_HOST = "localhost" # If running this script on your host machine to connect to Dockerized RabbitMQ
RABBITMQ_PORT = 5673
RABBITMQ_USER = "guest"
RABBITMQ_PASS = "guest"
INPUT_QUEUE = "rag_input_queue"

def send_test_message(transcription_text: str, conversation_id: str):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = None
    
    max_send_retries = 10 # Add retry mechanism for sending
    send_retry_delay = 2  # seconds
    
    for i in range(max_send_retries):
        try:
            print(f"Connecting to RabbitMQ to send message (Attempt {i+1}/{max_send_retries})...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials,
                    heartbeat=60 # Add heartbeat for robustness
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue=INPUT_QUEUE, durable=True)

            message = {
                "conversation_id": conversation_id,
                "transcription": transcription_text
            }

            channel.basic_publish(
                exchange='',
                routing_key=INPUT_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )
            print(f" [x] Sent message for conversation_id={conversation_id}")
            break # Break loop if successful
        except pika.exceptions.AMQPConnectionError as e:
            print(f"RabbitMQ connection failed on send: {e}. Retrying in {send_retry_delay} seconds...")
            time.sleep(send_retry_delay)
        except Exception as e:
            print(f"An unexpected error occurred while sending: {e}. Retrying in {send_retry_delay} seconds...")
            time.sleep(send_retry_delay)
        finally:
            if connection:
                try:
                    connection.close() # Close connection on each attempt or on success
                except Exception as close_e:
                    print(f"Error closing connection: {close_e}")
    else: # This block executes if the loop completes without a 'break'
        print(f"Failed to send message after {max_send_retries} attempts for conversation_id={conversation_id}.")

if __name__ == "__main__":
    test_transcription_1 = """
    Patient: Good morning, Doctor. I've been feeling quite tired lately, and I've had a persistent cough for about two weeks now.
    Doctor: Good morning. Can you tell me more about the cough? Is it dry or productive?
    Patient: It's mostly dry, but sometimes I get a little phlegm. It's worse at night. I also have a sore throat, but no fever.
    Doctor: Any shortness of breath or chest pain?
    Patient: No, just the cough and feeling run down. I've been taking some over-the-counter cough syrup, but it doesn't seem to help much.
    Doctor: Have you had any recent travel or exposure to sick individuals?
    Patient: No, nothing unusual.
    Doctor: Alright. Let's do a quick examination. I'll listen to your lungs.
    """
    test_transcription_2 = """
    Patient: My arm hurts, Doctor. I fell yesterday.
    Doctor: Where exactly does it hurt? Can you point to the spot?
    Patient: Right here, near my elbow. It's swollen and I can't really bend it fully.
    Doctor: Is there any numbness or tingling?
    Patient: No, just pain and stiffness.
    Doctor: Okay, we'll need an X-ray to check for a fracture.
    """

    print("Sending test message 1...")
    send_test_message(test_transcription_1, str(uuid.uuid4()))
    time.sleep(5) 
    print("Sending test message 2...")
    send_test_message(test_transcription_2, str(uuid.uuid4()))
    print("Done sending test messages.")