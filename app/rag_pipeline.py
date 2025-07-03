# # app/rag_pipeline.py
# import os
# from dotenv import load_dotenv
# from langchain_huggingface import HuggingFaceEndpoint
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# # Load environment variables (important if this file might be run standalone or tested separately)
# load_dotenv()

# def get_llm_client():
#     """Initializes and returns the HuggingFaceEndpoint LLM client connected to TGI."""
#     llm_api_url = os.getenv("LLM_API_URL")
#     hf_token = os.getenv("HF_TOKEN")

#     if not llm_api_url:
#         raise ValueError("LLM_API_URL environment variable not set in .env")
#     if not hf_token:
#         raise ValueError("HF_TOKEN environment variable not set in .env")

#     llm = HuggingFaceEndpoint(
#         endpoint_url=llm_api_url,
#         huggingfacehub_api_token=hf_token,
#         max_new_tokens=512,
#         temperature=0.1,
#         top_k=50,
#         top_p=0.95,
#         repetition_penalty=1.03,
#     )
#     return llm

# def get_summarization_chain():
#     """
#     Builds and returns the LangChain expression language chain for summarization.
#     """
#     llm = get_llm_client()

#     summary_template = """Patient Name:
# Date of Visit:
# Chief Complaint:
# Vital Signs:
# Patient History (new symptoms/concerns):
# Doctor's Assessment/Findings:
# Treatment Plan/Recommendations:
# Follow-up Schedule:"""

#     summarization_prompt_template = ChatPromptTemplate.from_messages(
#         [
#             ("system", """You are a highly skilled medical AI assistant specialized in summarizing doctor-patient conversations into a structured template. Your goal is to extract the most relevant information and present it clearly and concisely according to the provided template. If a piece of information is not mentioned in the conversation, state "Not specified" for that field. Do not invent information."""),
#             ("human", """Based on the following doctor-patient conversation, please summarize it using the provided template.

# ---
# Conversation:
# {conversation}
# ---

# Template:
# {template}
# ---
# Summary:
# """)
#         ]
#     )

#     # Combine prompt, LLM, and output parser into a chain
#     summarization_chain = summarization_prompt_template | llm | StrOutputParser()
#     return summarization_chain

# # You could add other chain-building functions here if your app grows, e.g., get_qa_chain()

# app/rag_pipeline.py
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough # Make sure this is imported

def get_summarization_chain():
    llm = HuggingFaceEndpoint(
        endpoint_url=os.getenv("TGI_ENDPOINT"),
        temperature=0.1, # Keep temperature low for factual summaries
        max_new_tokens=512, # Adjust as needed for summary length
        # Add custom_model_kwargs if necessary for Med42
        # e.g., custom_model_kwargs={"stop": ["Patient Name:", "Date of Visit:"]}
    )

    # UPDATED PROMPT TEMPLATE to use 'context' variable
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a highly skilled medical AI assistant specialized in summarizing doctor-patient conversations into a structured template. "
                "Your goal is to extract the most relevant information from the **provided context** and present it clearly and concisely according to the template. "
                "If a piece of information is not present **in the context**, state \"Not specified\" for that field. Do not invent information."
                "\n\nHere is the relevant context from the conversation:\n{context}" # <-- 'context' variable
            ),
            (
                "human",
                "Based on the following context, please summarize it using the provided template.\n"
                "---\nTemplate:\n{template}\n---\nSummary:"
            ),
        ]
    )

    # The chain now expects 'context' and 'template'
    return {"context": RunnablePassthrough(), "template": RunnablePassthrough()} | prompt_template | llm | StrOutputParser()