"""
Simple speech demo that records short clips (5s), sends them to Hamsa STT, asks OpenAI for a reply, and plays the answer via Hamsa TTS. Core pieces:
- `convert_audio_to_base64`: normalize WAV to 16 kHz mono and return Base64.
- `transcribe_audio`: call Hamsa STT with the Base64 audio.
- `generate_response`: async OpenAI chat with running history.
- `speak_text`: call Hamsa TTS and play with pygame.
- `record_audio`: fixed-duration mic capture (no VAD).
- `live_conversation`: loop until user says bye.

-voice used "Majd" you can use any voice from https://agents.tryhamsa.com/app/voices?sort=[{%22id%22:%22time%22,%22desc%22:true}]
"""
import sounddevice as sd
import wave
import io
import requests
import pygame
import io
import base64
import wave
import numpy as np
from pydub import AudioSegment
import os
import asyncio
from openai import AsyncOpenAI
import sounddevice as sd
from dotenv import load_dotenv

load_dotenv()

# Initialize async client with your API key from environment
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# -----------------------------
# Configuration
# -----------------------------

STT_URL = "https://api.tryhamsa.com/v1/realtime/stt"
TTS_URL = "https://api.tryhamsa.com/v1/realtime/tts"

STT_API_KEY = os.getenv("STT_API_KEY")
TTS_API_KEY = os.getenv("TTS_API_KEY")

# -----------------------------
# Convert audio file to Base64 PCM WAV
# -----------------------------
def convert_audio_to_base64(audio_input):
    try:
        # If audio_input is bytes, wrap in BytesIO
        if isinstance(audio_input, (bytes, bytearray)):
            buf = io.BytesIO(audio_input)
            audio = AudioSegment.from_wav(buf)
        else:
            # Otherwise assume it's a filename
            audio = AudioSegment.from_wav(audio_input)

        # Normalize to mono, 16‑bit, 16kHz
        audio = audio.set_channels(1).set_sample_width(2).set_frame_rate(16000)
        raw_audio_data = np.array(audio.get_array_of_samples())

        # Write to memory instead of disk
        buf_out = io.BytesIO()
        with wave.open(buf_out, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(raw_audio_data.tobytes())
        buf_out.seek(0)

        audio_bytes = buf_out.read()
        return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

# -----------------------------
# Speech-to-Text (STT)
# -----------------------------
def transcribe_audio(audio_input):
    audio_base64 = convert_audio_to_base64(audio_input)
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
# Keep history outside the function so it persists across calls
history = [{"role": "system", "content": "You are a helpful AI call assistant. Always reply with proper basic Arabic diacritical marks and language that matches the users ones."}]

"""
Cerebras streaming LLM response generator.
Replaces the OpenAI completion block.

Model used: gpt-oss-120b
"""

import os
from cerebras.cloud.sdk import Cerebras

cerebras_client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

async def generate_response(user_text: str) -> str:
    # Add user message to history
    history.append({"role": "user", "content": user_text})

    # Prepare messages in required format
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]

    # Create streaming completion request
    completion = cerebras_client.chat.completions.create(
        messages=messages,
        model="gpt-oss-120b",
        max_completion_tokens=1024,
        temperature=0.2,
        stream=False
    )

    # Collect and print streamed output
    full_text = ""

    # Add reply to history
    full_text=completion.choices[0].message.content
    history.append({"role": "assistant", "content": full_text})

    return full_text






# async def generate_response(user_text: str) -> str:
#     # Add user message to history
#     history.append({"role": "user","message":"you are a helpful assistant, reply naturally according to the user's language and dialect", "content": user_text})

#     # Call OpenAI asynchronously
#         # OLD MODEL COMPLETION - COMMENTED OUT
#     reply = await client.chat.completions.create(
#          model="gpt-oss-120b",
#          messages=history
#      )

#     # NEW MODEL (gpt-4o-mini)
#     response = await client.chat.completions.create(
#         model="gpt-4o-mini",  # or another model you prefer
#         messages=history
#     )

#     # Extract assistant reply
#     reply_text = response.choices[0].message.content

#     # Add assistant reply to history
#     history.append({"role": "assistant", "content": reply_text})


#     return reply_text

# -----------------------------
# Text-to-Speech (TTS)
# -----------------------------
def speak_text(text, speaker="Ahmed", dialect="egy"):
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
async def run_conversation(audio_file):
    user_text = transcribe_audio(audio_file)  # still synchronous STT
    if user_text:
        print("User said:", user_text)

        # Use async OpenAI response
        answer = await generate_response(user_text)
        print("Agent Response:", answer)

        # Speak back with TTS
        speak_text(answer)


def record_audio(duration=5, samplerate=16000):
    print("🎙️ Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    # Write directly to BytesIO
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())
    buf.seek(0)
    return buf.read()  # raw WAV bytes

async def live_conversation():
    while True:
        audio_bytes = record_audio()
        user_text = transcribe_audio(audio_bytes)
        if not user_text:
            continue

        print("User said:", user_text)

        # Fire OpenAI + TTS concurrently
        answer = await generate_response(user_text)
        print("Agent Response:", answer)

        # Speak while preparing next recording
        speak_text(answer)

        if any(kw in user_text.strip().lower() for kw in ["bye", "باي", "مع السلامة"]):
            print("👋 Conversation ended after AI reply.")
            break


# -----------------------------
# Run Example
# -----------------------------
if __name__ == "__main__":
    asyncio.run(live_conversation()) # Replace with your recorded audio file
