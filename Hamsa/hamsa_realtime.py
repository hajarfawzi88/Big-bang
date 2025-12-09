"""
This code represents a live interactive conversation system using voice input and output, powered by a combination of speech-to-text (STT), AI-based responses (via OpenAI), and text-to-speech (TTS). Here's a breakdown of its components and functionality:

1. **Configuration:**
   - **API URLs and Keys:** 
     - `STT_URL`: Endpoint for the speech-to-text API (Hamsa).
     - `TTS_URL`: Endpoint for the text-to-speech API (Hamsa).
     - API keys for both services are configured for access.
   - **Audio Settings:** 
     - `samplerate`: Sampling rate for audio input.
     - `frame_ms`: Frame size for speech processing.
     - `silence_ms`: Silence detection threshold to stop recording.

2. **Audio Utilities:**
   - **`pcm_frames_to_wav_bytes(pcm_frames)`**: Converts raw PCM audio frames to WAV format (in-memory), which is then used for processing or API interaction.
   - **`record_audio_continuous()`**: Continuously records audio using `sounddevice` and processes it with WebRTC Voice Activity Detection (VAD). The VAD distinguishes between speech and silence to manage audio recording duration.

3. **Speech-to-Text (STT) Conversion:**
   - **`transcribe_audio_bytes(wav_bytes)`**: Sends the recorded audio (in WAV format) to the Hamsa STT service, which transcribes it into text. It uses Base64 encoding to send the audio data as part of the POST request.

4. **AI Interaction (OpenAI):**
   - **`generate_response(user_text)`**: This function sends the transcribed user text to OpenAI’s GPT model (`gpt-4o-mini`), generating a response based on the conversation history.

5. **Text-to-Speech (TTS) Output:**
   - **`speak_text(text, speaker="Majd", dialect="egy")`**: This function sends the generated response to the TTS API and plays the resulting speech using the `pygame` mixer. The speech can be customized with different speakers and dialects.

6. **Conversation Loop:**
   - **`live_conversation()`**: The main loop of the system, which continuously records audio, converts it to text, generates a response from OpenAI, and plays the response out loud. The loop continues until the user ends the conversation by saying "bye" or a similar farewell phrase.

7. **Run:**
   - The system starts the conversation loop by invoking `asyncio.run(live_conversation())`.

This system allows for real-time, interactive voice-based conversations with AI, handling both speech recognition and speech synthesis seamlessly.
"""



import os
import io
import wave
import base64
import asyncio
import requests
import pygame
import sounddevice as sd
import webrtcvad
import numpy as np
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Config
# -----------------------------
STT_URL = "https://api.tryhamsa.com/v1/realtime/stt"
TTS_URL = "https://api.tryhamsa.com/v1/realtime/tts"

STT_API_KEY = os.getenv("STT_API_KEY")
TTS_API_KEY = os.getenv("TTS_API_KEY")
samplerate = 16000
frame_ms = 10          # Frame size in ms (must be 10, 20, or 30 for VAD)
silence_ms = 500      # Stop after ~1s of silence
vad = webrtcvad.Vad(2)  # VAD aggressiveness: 0–3 (higher = more sensitive)

# OpenAI client (read from environment)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize pygame mixer once
pygame.mixer.init(frequency=16000)

# -----------------------------
# Audio utils
# -----------------------------
def pcm_frames_to_wav_bytes(pcm_frames: np.ndarray, samplerate: int = 16000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(samplerate)
        wf.writeframes(pcm_frames.tobytes())
    buf.seek(0)
    return buf.read()

def record_audio_continuous():
    print("🎙️ Listening... start speaking")

    frame_size = int(samplerate * frame_ms / 1000)  # Samples per frame
    audio_frames = []
    continuous_silence_ms = 0

    def callback(indata, frames, time, status):
        nonlocal audio_frames, continuous_silence_ms
        if status:
            print(status)

        pcm = indata[:, 0].copy()  # Mono audio channel
        audio_frames.append(pcm)

        # VAD expects bytes, so check if speech is detected
        is_speech = vad.is_speech(pcm.tobytes(), samplerate)

        if is_speech:
            continuous_silence_ms = 0  # Reset silence counter when speech is detected
        else:
            continuous_silence_ms += frame_ms  # Increment silence duration

        # Continue recording if there's speech, else stop after silence
        if continuous_silence_ms >= silence_ms:
            pass

    try:
        # Start the recording stream with specified parameters
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16',
                            blocksize=frame_size, callback=callback):
            sd.sleep(1000000000)  # Keep listening indefinitely

    except Exception as e:
        print(f"Error in audio recording: {e}")
        pass

    # Combine all frames into a single audio array
    audio = np.concatenate(audio_frames, axis=0)
    
    # Convert audio frames to WAV format in memory
    wav_bytes = pcm_frames_to_wav_bytes(audio, samplerate)

    return wav_bytes


# -----------------------------
# STT
# -----------------------------
def transcribe_audio_bytes(wav_bytes: bytes) -> str | None:
    """Send PCM WAV bytes to Hamsa STT (Base64) and return text."""
    audio_base64 = base64.b64encode(wav_bytes).decode("utf-8")
    payload = {
        "audioBase64": audio_base64,
        "language": "ar",
        "isEosEnabled": False,
        "eosThreshold": 0.3
    }
    headers = {"Authorization": f"Token {STT_API_KEY}", "Content-Type": "application/json"}

    resp = requests.post(STT_URL, json=payload, headers=headers)
    if resp.status_code == 200:
        result = resp.json()
        print("STT Result:", result)
        return result.get("data", {}).get("text", "")
    else:
        print("STT Error:", resp.text)
        return None


# -----------------------------
# OpenAI response (with history)
# -----------------------------
history = [{"role": "system", "content": "You are a helpful AI call assistant. Reply naturally in Arabic."}]

async def generate_response(user_text: str) -> str:
    history.append({"role": "user", "content": user_text})
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history,
    )
    reply_text = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply_text})
    return reply_text


# -----------------------------
# TTS
# -----------------------------
def speak_text(text: str, speaker: str = "Majd", dialect: str = "egy"):
    payload = {
        "text": text,
        "speaker": speaker,
        "dialect": dialect,
        "mulaw": False
    }
    headers = {"Authorization": f"Token {TTS_API_KEY}", "Content-Type": "application/json"}
    resp = requests.post(TTS_URL, json=payload, headers=headers)

    if resp.status_code == 200:
        # Try JSON with base64 first; fallback to raw audio
        audio_data = None
        try:
            result = resp.json()
            if "audioBase64" in result:
                audio_data = base64.b64decode(result["audioBase64"])
        except ValueError:
            audio_data = resp.content

        if not audio_data:
            print("Unexpected TTS response format:", resp.text[:200])
            return

        sound = pygame.mixer.Sound(io.BytesIO(audio_data))
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)
        print("🔊 TTS played successfully.")
    else:
        print("TTS Error:", resp.text)


# -----------------------------
# Conversation loop with VAD
# -----------------------------
async def live_conversation():
    while True:
        wav_bytes = record_audio_continuous()  # Returns in-memory WAV bytes
        user_text = transcribe_audio_bytes(wav_bytes)  # Send directly to STT
        if not user_text:
            continue

        print("User said:", user_text)

        answer = await generate_response(user_text)
        print("Agent Response:", answer)
        speak_text(answer)

        user_l = user_text.strip().lower()
        if ("bye" in user_l) or ("باي" in user_l) or ("مع السلامة" in user_l):
            print("👋 Conversation ended after AI reply.")
            break


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    asyncio.run(live_conversation())  # Continuous conversation loop
