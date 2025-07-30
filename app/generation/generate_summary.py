import requests
import json
from typing import List, Dict, Any

def generate_summary(
    transcribed_conversation: str,
    relevant_knowledge_chunks: List[Dict[str, Any]],
    tgi_service_url: str,
    max_new_tokens: int = 3000,
    temperature: float = 0.2
) -> str:
    """
    Generates a templated clinical summary using the TGI service (Med 42 LLM).

    Args:
        relevant_chunks (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
                                                represents a retrieved chunk with 'page_content'.
        query (str): The original user query.
        tgi_service_url (str): The URL of the TGI service (e.g., "http://tgi_service:8080").
        max_new_tokens (int): The maximum number of tokens to generate in the summary.
        temperature (float): Controls the randomness of the generation. Lower values make it more deterministic.

    Returns:
        str: The generated clinical summary, or an empty string if generation fails.
    """
    if not transcribed_conversation.strip():
        return "No transcribed conversation provided to generate a summary."

    # Construct the prompt for the LLM.
    context = "\n".join([chunk["page_content"] for chunk in relevant_knowledge_chunks])
    if context: 
        context = f"""
        ---Relevant Clinical Guidelines/Knowledge---
        {context}
        ---End Relevant Clinical Guidelines/Knowledge---
        """
    else:
        context = "No specific external clinical guidelines were returned"

    # Example of a structured prompt for a clinical summary
    # prompt = f"""
    # You are an AI assistant specialized in medical summarization. Your task is to generate a concise, templated clinical summary based on the provided patient conversation (context) and the user's query.

    # **Example of desired output format:**
    # Presenting complaint: Patient reports a cough.
    # History of presenting complaint: Cough started 3 days ago, non-productive.
    # Family history: High cholesterol runs in the family.
    # Past surgical history: Information not provided.

    # Template to follow is below
    
    # Presenting complaint:
    # History of presenting complaint:
    # Review of systems:
    # Past medical history:
    # Past surgical history:
    # Drug history:
    # Family history:
    # Social history:
    # Observation:
    # Assessment:
    # Clinical impression/Differential diagnosis:
    # Plan of Action:

    # **Patient Doctor Conversation:**
    # {transcribed_conversation}
    # {context}

    # Please generate the clinical summary. Do not make up any information.
    # If there is no relevant information for a section, you MUST output the section title followed by "Information not provided.".
    # For example, if no information is available for "Past surgical history", you would write:
    # Past surgical history: Information not provided.

    # Ensure ALL section titles from the template are present in your final summary.
    # """
    prompt = f"""
    You are an AI assistant specialized in medical summarization. Your task is to generate a concise, templated clinical summary based on the provided patient conversation (context) and the user's query.

    **VERY IMPORTANT: The entire summary MUST be formatted using Markdown.**
    **Use bolding for ALL section titles (e.g., **Presenting complaint:**).**
    **Use bullet points for lists where appropriate (e.g., Review of systems).**
    **Use double newlines (empty lines) between each section to ensure proper paragraph breaks in Markdown.**

    **Example of desired output format:**
    **Presenting complaint:** Patient reports a cough.\n\n

    **History of presenting complaint:** Cough started 3 days ago, non-productive.\n\n

    **Family history:** High cholesterol runs in the family.\n\n

    **Past surgical history:** Information not provided.\n\n

    **Template to follow is below (ensure ALL titles are bolded and followed by double newlines):**

    **Presenting complaint:**\n\n

    **History of presenting complaint:**\n\n

    **Review of systems:**\n\n
    **Past medical history:**\n\n
    **Past surgical history:**\n\n
    **Drug history:**\n\n
    **Family history:**\n\n
    **Social history:**\n\n
    **Observation:**\n\n
    **Assessment:**\n\n\
    **Clinical impression/Differential diagnosis:**\n\n
    **Plan of Action:**\n\n
    

    **Patient Doctor Conversation:**
    {transcribed_conversation}
    {context}

    Please generate the clinical summary following the exact template and formatting instructions. Do not make up any information.
    If there is no relevant information for a section, you MUST output the section title (bolded) followed by "Information not provided.".
    For example, if no information is available for "Past surgical history", you would write:
    **Past surgical history:** Information not provided.\n\n

    Ensure ALL section titles from the template are present in your final summary and bolded.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "do_sample": temperature > 0, # Only sample if temperature is > 0
            "return_full_text": False 
        }
    }

    try:
        print(f"Sending request to TGI URL: {tgi_service_url}/generate")
        print(f"Payload being sent: {json.dumps(payload, indent=2)}")
        response = requests.post(f"{tgi_service_url}/generate", headers=headers, data=json.dumps(payload))
        
        print(f"TGI Response Status Code: {response.status_code}")
        print(f"TGI Raw Response Text: {response.text}")
        
        response.raise_for_status() # Raise an exception for HTTP errors

        response_data = response.json()
        print(f"TGI Parsed JSON Response: {json.dumps(response_data, indent=2)}")
        if isinstance(response_data, dict) and 'generated_text' in response_data:
            # TGI typically returns a list of results, each with 'generated_text'
            generated_text = response_data["generated_text"]
            return generated_text
        else:
            print("TGI service returned an unexpected response format.")
            print(f"Full JSON response: {json.dumps(response_data, indent=2)}")
            return ""

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with TGI service: {e}")
        return ""
    except json.JSONDecodeError:
        print("Failed to decode JSON response from TGI service.")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred during summary generation: {e}")
        return ""
