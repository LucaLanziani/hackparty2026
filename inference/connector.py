import os
from utils import call_nim_api, call_nim_api_async

PROMPT = """
you are a classifier for a ticketing system
classify the ticket in one of the following categories:

task:  General work item
Bug:  Defect / error
Enhancement:  Feature extension
Research:  Investigation / feasibility
Design:  UI/UX / mockup
Testing:  QA / validation
Deployment:  Release / infra / CI-CD
Documentation:  Docs / guide

Reply with only the category name (e.g. Bug, task, Enhancement).

"""


def build_messages_for_ticket(ticket_content: str) -> list[dict]:
    """Append ticket content to the classification prompt."""
    full_content = PROMPT.strip() + "\n\n---\nTicket to classify:\n\n" + (ticket_content or "").strip()
    return [{"role": "user", "content": full_content}]

def create_llm_payload(model, messages, **kwargs):
    """
    Create a payload for an NVIDIA NIM API call to an LLM.

    Args:
        model (str): The model to use.
        messages (list): List of message dictionaries.
        **kwargs: Arbitrary keyword arguments for additional payload parameters.

    Returns:
        dict: The payload for the API call.
    """
    # Default values
    default_params = {
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 1024,
        "stream": False
    }

    # Update default parameters with any provided kwargs
    default_params.update(kwargs)

    # Create the payload
    payload = {
        "model": model,
        "messages": messages,
        **default_params
    }

    return payload


def parse_classification_response(response: dict) -> str:
    """Extract classification text from NIM chat response."""
    try:
        return (response["choices"][0]["message"]["content"] or "").strip()
    except (KeyError, IndexError, TypeError):
        return ""


def print_response(response):
    content = parse_classification_response(response)
    if content:
        print(content)
    else:
        print("Error: Unable to find the expected content in the response.")


# Hosted API: https://integrate.api.nvidia.com/v1/chat/completions (OpenAI-compatible)
LLM_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-3.1-8b-instruct"


async def classify_ticket(ticket_content: str, api_key: str) -> dict:
    """
    Classify a ticket by appending its content to the prompt and calling the LLM.
    Returns dict with 'classification' (str) and optionally 'raw_response'.
    """
    messages = build_messages_for_ticket(ticket_content)
    payload = create_llm_payload(MODEL, messages)
    response = await call_nim_api_async(LLM_ENDPOINT, payload, api_key=api_key)
    classification = parse_classification_response(response)
    return {"classification": classification, "raw_response": response}


if __name__ == "__main__":
    import asyncio
    async def _demo():
        key = os.getenv("NVIDIA_API_KEY")
        result = await classify_ticket("The login button returns 500 when clicked.", api_key=key or "")
        print(result["classification"])
    asyncio.run(_demo())