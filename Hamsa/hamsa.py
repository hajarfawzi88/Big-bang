import requests
import pygame
import io
import base64
import wave
import numpy as np
from pydub import AudioSegment

# -----------------------------
# Configuration
# -----------------------------
STT_URL = "https://api.tryhamsa.com/v1/realtime/stt"
TTS_URL = "https://api.tryhamsa.com/v1/realtime/tts"

STT_API_KEY = "9e769996-f062-4362-b005-1b359b42ccd8"   # Replace with your STT API key
TTS_API_KEY = "9e769996-f062-4362-b005-1b359b42ccd8"   # Replace with your TTS API key

# -----------------------------
# Convert audio file to Base64 PCM WAV
# -----------------------------
def convert_audio_to_base64(audio_file):
    try:
        audio = AudioSegment.from_wav(audio_file)
        audio = audio.set_channels(1).set_sample_width(2).set_frame_rate(16000)
        raw_audio_data = np.array(audio.get_array_of_samples())

        with wave.open("processed.wav", "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(raw_audio_data.tobytes())

        with open("processed.wav", "rb") as wf:
            audio_bytes = wf.read()

        return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

# -----------------------------
# Speech-to-Text (STT)
# -----------------------------
def transcribe_audio(audio_file):
    audio_base64 = convert_audio_to_base64(audio_file)
    if not audio_base64:
        return None

    payload = {
        "audioBase64": audio_base64,
        "language": "ar",
        "isEosEnabled": False,
        "eosThreshold": 0.3
    }
    headers = {"Authorization": f"Token {STT_API_KEY}", "Content-Type": "application/json"}

    response = requests.post(STT_URL, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print("STT Result:", result)
        return result.get("data", {}).get("text", "")
    else:
        print("STT Error:", response.text)
        return None

# -----------------------------
# Generate Response
# -----------------------------
def generate_response(user_text):
    print("generating")
    return f"You said: {user_text}. How can I help you?"

# -----------------------------
# Text-to-Speech (TTS)
# -----------------------------
def speak_text(text, speaker="Noura", dialect="msa"):
    payload = {
        "text": text,
        "speaker": speaker,
        "dialect": dialect,
        "mulaw": False
    }
    headers = {"Authorization": f"Token {TTS_API_KEY}", "Content-Type": "application/json"}

    response = requests.post(TTS_URL, json=payload, headers=headers)

    if response.status_code == 200:
        try:
            # Try to parse JSON first
            result = response.json()
            if "audioBase64" in result:
                audio_data = base64.b64decode(result["audioBase64"])
            else:
                print("Unexpected JSON:", result)
                return
        except Exception:
            # If not JSON, assume raw audio bytes
            audio_data = response.content

        # Initialize mixer with correct sample rate
        pygame.mixer.init(frequency=16000)
        sound = pygame.mixer.Sound(io.BytesIO(audio_data))
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)
        print("TTS played successfully.")
    else:
        print("TTS Error:", response.text)


# -----------------------------
# Main Conversation Flow
# -----------------------------
def run_conversation(audio_file):
    user_text = transcribe_audio(audio_file)
    print(user_text)
    if user_text:
        answer = generate_response(user_text)
        print("Agent Response:", answer)
        speak_text(answer)

# -----------------------------
# Run Example
# -----------------------------
if __name__ == "__main__":
    run_conversation("output.wav")  # Replace with your recorded audio file
