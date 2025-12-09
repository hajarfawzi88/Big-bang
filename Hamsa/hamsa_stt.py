"""
This code demonstrates how to convert an audio file into Base64 format, send it to a Speech-to-Text (STT) service (Hamsa API), and handle the response. Here's an overview of each component:

1. **Configuring the API and File Paths:**
   - The Hamsa API URL (`url`) and API key (`API_KEY`) are configured for the Speech-to-Text request.
   - `audio_file` refers to the recorded WAV audio file that will be converted and sent for transcription.

2. **`convert_audio_to_base64()` function:**
   - This function performs the following tasks:
     - **Load Audio:** The audio file is loaded using the `pydub` library.
     - **Mono Conversion:** If the audio file is stereo, it converts it to mono channel for uniformity.
     - **Audio Formatting:** The sample width is set to 16-bit, and the frame rate is set to 16 kHz to ensure compatibility with the STT service.
     - **Save as WAV:** The processed audio is saved as a valid PCM WAV file, making it compatible with the STT service.
     - **Base64 Encoding:** The WAV file is read and converted into Base64 encoding, which is required for the STT service to process it.

3. **Sending the Audio to the STT Service:**
   - After converting the audio to Base64, the payload for the STT request is created with the necessary parameters, including the encoded audio and language (`"ar"` for Arabic).
   - A POST request is sent to the Hamsa API with the payload and the authorization header containing the API key.

4. **Response Handling:**
   - If the STT request is successful, the transcribed text (if available) is printed. If there is an error, the error message is displayed.

5. **Usage:**
   - The function `convert_audio_to_base64(audio_file)` is called with the path to the audio file (in this case `"output.wav"`).
   - The function returns the Base64-encoded audio, which is used in the payload to send to the STT service for transcription.

This code allows you to send audio data in Base64 format to the Hamsa Speech-to-Text API, which processes the audio and returns the transcribed text in Arabic.
"""

import requests
import base64
import wave
import numpy as np
from pydub import AudioSegment

# Hamsa API URL and Authorization
url = "https://api.tryhamsa.com/v1/realtime/stt"
API_KEY = "9e769996-f062-4362-b005-1b359b42ccd8"

# Function to Convert Audio to Base64 and Save as Valid PCM WAV
def convert_audio_to_base64(audio_file):
    try:
        # Load the audio file with pydub
        audio = AudioSegment.from_wav(audio_file)

        # Convert to mono channel if stereo
        audio = audio.set_channels(1)

        # Set the sample width to 2 bytes (16-bit)
        audio = audio.set_sample_width(2)

        # Set the sample rate to 16,000 Hz
        audio = audio.set_frame_rate(16000)

        # Save the WAV file explicitly as raw PCM
        raw_audio_data = np.array(audio.get_array_of_samples())

        # Create a new WAV file with raw PCM data using wave module
        with wave.open("output_processed_pcm.wav", "wb") as wf:
            wf.setnchannels(1)  # Mono channel
            wf.setsampwidth(2)  # 2 bytes for 16-bit sample width
            wf.setframerate(16000)  # 16 kHz sample rate
            wf.writeframes(raw_audio_data.tobytes())  # Write PCM data to the file
        
        print("Audio file exported as valid PCM WAV format.")

        # Export raw audio data (Base64 encode the WAV file)
        with open("output_processed_pcm.wav", "rb") as wf:
            audio_bytes = wf.read()

        # Encode the audio data as Base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        print("Audio converted to Base64 format.")
        return audio_base64
    except Exception as e:
        print(f"Error converting audio to Base64: {e}")
        return None

# Path to the recorded audio file
audio_file = "output.wav"  # Ensure this file exists and is the correct format

# Convert audio to Base64
audio_base64 = convert_audio_to_base64(audio_file)

if audio_base64:
    # Set up payload with the correct data
    payload = {
        "audioBase64": audio_base64,  # Use Base64-encoded audio
        "language": "ar",             # Language (Arabic in this case)
        "isEosEnabled": False,        # EOS (End of Speech) detection (optional)
        "eosThreshold": 0.3           # EOS Threshold (optional)
    }
    
    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json"
    }

    # Send the POST request
    response = requests.post(url, json=payload, headers=headers)

    # Check the response
    if response.status_code == 200:
        print("STT Success:")
        print(response.json())  # Print the response from the API
    else:
        print(f"Error with Speech-to-Text: {response.text}")
