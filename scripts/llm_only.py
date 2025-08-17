# scripts/llm_only.py

import os
import sys
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.generation.generate_summary import generate_summary

def main():
    parser = argparse.ArgumentParser(
        description="Generate a clinical summary using the Med 42 LLM."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a text file containing the transcribed conversation."
    )
    parser.add_argument(
        "--conversation",
        type=str,
        help="Direct conversation string to summarize."
    )
    parser.add_argument(
        "--additional",
        type=str,
        default="",
        help="Optional additional notes to include in the summary."
    )
    parser.add_argument(
        "--tgi-url",
        type=str,
        default=os.environ.get("TGI_SERVICE_URL", "http://localhost:80"),
        help="TGI service URL (default from TGI_SERVICE_URL env var or http://localhost:80)."
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2000,
        help="Maximum number of tokens for LLM generation."
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature for generation."
    )

    args = parser.parse_args()

    # Load conversation from file if provided, else use direct string
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' does not exist.")
            return
        with open(args.file, "r") as f:
            transcribed_conversation = f.read()
    elif args.conversation:
        transcribed_conversation = args.conversation
    else:
        print("Error: Please provide a conversation via --file or --conversation.")
        return

    summary = generate_summary(
        transcribed_conversation=transcribed_conversation,
        relevant_knowledge_chunks=[],  # LLM-only mode
        tgi_service_url=args.tgi_url,
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
        additional_content=args.additional
    )

    print("\n=== Generated Clinical Summary ===\n")
    print(summary)


if __name__ == "__main__":
    main()
