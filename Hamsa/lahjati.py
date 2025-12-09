import os
import requests
import pyaudio
import subprocess
from io import BytesIO

# Set your Lahajati API key and other parameters
API_KEY = "sk_eyJpdiI6Im91ajh4TDI3ZUt0YlZaUTFiRGJxRnc9PSIsInZhbHVlIjoiMDN3bHd2Nkd3VE5ZelpUTnVGY1VVaG9TVjFZaE9pRGRiVitZRXBJZzk3bGRkc0RzYld0SFZyQUk2cGtwNUZhdCIsIm1hYyI6ImE5NTVkOTA4ZTMyNzk3ZDlmZDlmNGYyODIxZjQ0MDRjNzM2NDJlM2U4YTUyOTFiYzExYzZlNzQxMjE3MTRhZDgiLCJ0YWciOiIifQ=="
VOICE_ID = "xKcZnBxPAaPGv5lHHVErx1xT"  # Example: replace with your valid voice ID
PERF_ID = "3"  # Example: replace with your valid performance ID
DIALECT_ID = "10"  # Example: replace with your valid dialect ID

API_URL = "https://lahajati.ai/api/v1/text-to-speech-absolute-control"

# Function to play audio directly using pyaudio
def play_audio(audio_data):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,  # Ensure the sample rate is 16 kHz
                    output=True)
    
    # Write audio to stream
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()
    p.terminate()

# Function to send text to Lahajati and get the TTS audio response, playing it in real time
def text_to_speech_real_time(text: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    
    payload = {
        "text": text,
        "id_voice": VOICE_ID,
        "input_mode": "0",  # structured mode
        "performance_id": PERF_ID,
        "dialect_id": DIALECT_ID
    }

    # Send the request to the Lahajati API
    print("Sending request to Lahajati...")
    resp = requests.post(API_URL, headers=headers, json=payload, stream=True)

    # Raise an exception if the request fails
    resp.raise_for_status()

    # Convert the MP3 response to WAV using ffmpeg (in-memory, no temporary files)
    audio_data = b""
    for chunk in resp.iter_content(chunk_size=8192):
        if chunk:
            audio_data += chunk

    # Use ffmpeg to convert the MP3 data to WAV in-memory via pipe, with 16kHz mono conversion
    print("Converting MP3 to WAV in-memory using ffmpeg...")
    process = subprocess.Popen(
        ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', '-ar', '16000', '-ac', '1', 'pipe:1'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Pass the MP3 data to ffmpeg's stdin and get the WAV data from stdout
    wav_data, _ = process.communicate(input=audio_data)

    # Play the converted WAV audio
    print("Playing audio...")
    play_audio(wav_data)

# Example usage of the function
if __name__ == "__main__":
    sample_text = "السلام عليكم، هذا اختبار للصوت الاصطناعي من لهجاتي."
    text_to_speech_real_time(sample_text)
