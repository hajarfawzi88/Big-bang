import requests
import base64
import wave
import numpy as np
from pydub import AudioSegment
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("STT_key")
HAMSA_STT_URL = "https://api.tryhamsa.com/v1/realtime/stt"


def prepare_audio_base64(audio_path: str) -> str:
    """
    Load a WAV file, normalize it to 16-kHz mono PCM, and return Base64-encoded audio.

    Args:
        audio_path (str): Path to the input WAV file.

    Returns:
        str: Base64-encoded audio data ready for Hamsa STT API.

    Raises:
        Exception: If audio loading or conversion fails.
    """
    try:
        audio = AudioSegment.from_wav(audio_path)

        # Ensure correct format: mono, 16-bit, 16 kHz
        audio = (
            audio.set_channels(1)
                 .set_sample_width(2)
                 .set_frame_rate(16000)
        )

        pcm_data = np.array(audio.get_array_of_samples())

        # Save as proper raw PCM WAV temporarily
        tmp_output = "processed_pcm.wav"
        with wave.open(tmp_output, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm_data.tobytes())

        with open(tmp_output, "rb") as wf:
            audio_bytes = wf.read()

        return base64.b64encode(audio_bytes).decode("utf-8")

    except Exception as e:
        raise Exception(f"Audio processing failed: {e}")


def hamsa_stt(audio_path: str, language: str = "ar") -> dict:
    """
    Perform speech-to-text using the Hamsa STT API.

    Args:
        audio_path (str): Local WAV file to transcribe (any format; will be normalized).
        language (str): Language code for recognition (e.g., 'ar').

    Returns:
        dict: Transcription result from the API.

    Raises:
        Exception: If API call fails or invalid response received.
    """
    audio_b64 = prepare_audio_base64(audio_path)

    payload = {
        "audioBase64": audio_b64,
        "language": language,
        "isEosEnabled": False,
        "eosThreshold": 0.3
    }

    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(HAMSA_STT_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Hamsa STT Error {response.status_code}: {response.text[:200]}")
