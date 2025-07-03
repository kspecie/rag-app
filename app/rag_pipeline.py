# app/rag_pipeline.py
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables (important if this file might be run standalone or tested separately)
load_dotenv()

def get_llm_client():
    """Initializes and returns the HuggingFaceEndpoint LLM client connected to TGI."""
    llm_api_url = os.getenv("LLM_API_URL")
    hf_token = os.getenv("HF_TOKEN")

    if not llm_api_url:
        raise ValueError("LLM_API_URL environment variable not set in .env")
    if not hf_token:
        raise ValueError("HF_TOKEN environment variable not set in .env")

    llm = HuggingFaceEndpoint(
        endpoint_url=llm_api_url,
        huggingfacehub_api_token=hf_token,
        max_new_tokens=512,
        temperature=0.1,
        top_k=50,
        top_p=0.95,
        repetition_penalty=1.03,
    )
    return llm

def get_summarization_chain():
    """
    Builds and returns the LangChain expression language chain for summarization.
    """
    llm = get_llm_client()

    summary_template = """Patient Name:
Date of Visit:
Chief Complaint:
Vital Signs:
Patient History (new symptoms/concerns):
Doctor's Assessment/Findings:
Treatment Plan/Recommendations:
Follow-up Schedule:"""

    summarization_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", """You are a highly skilled medical AI assistant specialized in summarizing doctor-patient conversations into a structured template. Your goal is to extract the most relevant information and present it clearly and concisely according to the provided template. If a piece of information is not mentioned in the conversation, state "Not specified" for that field. Do not invent information."""),
            ("human", """Based on the following doctor-patient conversation, please summarize it using the provided template.

---
Conversation:
{conversation}
---

Template:
{template}
---
Summary:
""")
        ]
    )

    # Combine prompt, LLM, and output parser into a chain
    summarization_chain = summarization_prompt_template | llm | StrOutputParser()
    return summarization_chain

# You could add other chain-building functions here if your app grows, e.g., get_qa_chain()