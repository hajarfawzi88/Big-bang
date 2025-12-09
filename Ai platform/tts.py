import requests
import io
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("TTS_key")

def hamsa_tts(text: str, speaker: str = "Noura", dialect: str = "pls", mulaw: bool = False) -> bytes:
    """
    Generate speech audio using the Hamsa TTS API.

    Args:
        text (str): The text to synthesize into speech.
        speaker (str): Voice model to use (e.g., "Noura", "Adam").
        dialect (str): Arabic dialect code supported by Hamsa (e.g., "pls").
        mulaw (bool): Whether to return µ-law encoded audio.

    Returns:
        bytes: Raw audio bytes returned by the API.
               The MCP client or UI can choose how to play or store it.

    Raises:
        Exception: If the API call fails or returns a non-200 status.
    """

    url = "https://api.tryhamsa.com/v1/realtime/tts"

    payload = {
        "text": text,
        "speaker": speaker,
        "dialect": dialect,
        "mulaw": mulaw
    }

    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.content  # raw audio bytes
    else:
        raise Exception(
            f"TTS request failed: {response.status_code} - {response.text[:200]}"
        )
