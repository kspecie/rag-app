import requests
import json
from typing import List, Dict, Any, Optional
from scripts.save_summary import save_summary_to_db
import uuid

def generate_summary(
    transcribed_conversation: str,
    relevant_knowledge_chunks: List[Dict[str, Any]],
    tgi_service_url: str,
    max_new_tokens: int = 2000,
    temperature: float = 0.2,
    additional_content: Optional[str] = None 
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


    extra_notes = ""
    if additional_content and additional_content.strip():
        extra_notes = f"\n\n**Additional User Notes:**\n{additional_content.strip()}\n"

    
    prompt = f"""

    ### Instruction
    I am a medical doctor and I need you to generate a concise, templated History and Physical (H&P) clinical summary based on the provided patient-doctor conversation (transcribed_conversation). Include any extra information (extra_notes) and leverage any relevant information (context).

    ###

    Example of desired output format:
        **Presenting complaint:** Patient reports a cough.
        **History of presenting complaint:** Cough started 3 days ago, non-productive.
        **Family history:** High cholesterol runs in the family.
        **Past surgical history:** Information not provided.

    Template to follow is below (ALL titles are bolded):
        **Presenting Complaint:**
        **History of Presenting Complaint:**
        **Review of Systems:**
        **Past Medical History:**
        **Past Surgical History:**
        **Drug History:**
        **Family History:**
        **Social History:**
        **Observation:**
        **Assessment:**
        **Clinical Impression/Differential Diagnosis:**
        **Plan of Action:**

    Input Data:
    {transcribed_conversation}
    {extra_notes}
    {context}

    Important instructions for output:
        • Do not makeup any information
        • If no relevant information is available for a section, output the section title (bolded) followed by: "Information not provided."
            ○ Example:
                § **Past Surgical History:** Information not provided.
        • Ensure all section titles from the template are included in the generated summary and bolded.

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
        #print(f"TGI Raw Response Text: {response.text}")
        
        response.raise_for_status() # Raise an exception for HTTP errors

        response_data = response.json()
        #print(f"TGI Parsed JSON Response: {json.dumps(response_data, indent=2)}")
        if isinstance(response_data, dict) and 'generated_text' in response_data:
            # TGI typically returns a list of results, each with 'generated_text'
            generated_text = response_data["generated_text"]
            summary_id = str(uuid.uuid4())
            summary_data = {
                'id': summary_id,
                'title': 'Clinical Summary',
                'content': generated_text
            }
            save_summary_to_db(summary_data)
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
