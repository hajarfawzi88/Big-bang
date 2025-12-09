"""
This script demonstrates how to send text to a Text-to-Speech (TTS) service (Hamsa API), convert it into speech, and play it using Pygame.

### Components of the code:

1. **Configuring the API and Authorization:**
   - The Hamsa TTS API URL (`url`) and API key (`Authorization` header) are configured for sending the TTS request.
   - `payload` contains the parameters required by the TTS API, including:
     - `text`: The text you want to convert into speech (in Arabic).
     - `speaker`: Specifies the voice of the speaker (e.g., "Noura").
     - `dialect`: The dialect of the speech (e.g., "pls" for Palestinian).
     - `mulaw`: A parameter for pitch/loudness control (set to `False` here).

2. **Sending the Request:**
   - The code sends a `POST` request to the TTS API, passing the `payload` and the `Authorization` header to authenticate the request.

3. **Handling the Response:**
   - If the response from the TTS service is successful (status code 200), it contains raw audio data in the response body.
   - The raw audio content is extracted (`response.content`) and used to play the generated speech.

4. **Audio Playback with Pygame:**
   - Pygame is initialized to handle audio playback (`pygame.mixer.init()`).
   - The raw audio data is loaded into Pygame using `pygame.mixer.Sound()` and played using `sound.play()`.
   - The script waits until the audio finishes playing before moving forward (`while pygame.mixer.get_busy()`).

5. **Error Handling:**
   - If there’s an issue with the response (non-200 status code or error in playing audio), appropriate error messages are printed.

### Usage:
- The script sends an Arabic text `"مرحباً بكم في جميعاً في"` to the TTS API, which converts the text into speech using the "Noura" voice and the specified dialect.
- The generated speech is then played using Pygame.

This code effectively integrates TTS functionality with Pygame for speech playback, allowing real-time generation and playback of speech from text.
"""

import requests
import pygame
import io

# Hamsa API URL and Authorization
url = "https://api.tryhamsa.com/v1/realtime/tts"

# The payload containing the text, speaker, dialect, and other options
payload = {
    "text": "مرحباً بكم في جميعاً في",  # Example text
    "speaker": "Noura",  # Speaker to be used for TTS
    "dialect": "pls",  # Arabic dialect (ensure that this dialect is available)
    "mulaw": False  # Optional parameter, ensure it's valid
}

# Headers for the API request, including the authorization token
headers = {
    "Authorization": "Token 4e7ef1ea-5bf4-4e87-9b54-6c8b9ead1f93",  # Replace with your API token
    "Content-Type": "application/json"
}

# Sending the POST request to the TTS API
response = requests.post(url, json=payload, headers=headers)

# Check if the response is OK
if response.status_code == 200:
    print("Response Headers:", response.headers)

    try:
        # The response is in audio format, not JSON
        audio_data = response.content  # Get the raw audio content
        
        # Initialize Pygame for audio playback
        pygame.mixer.init()

        # Play the audio from the raw bytes
        sound = pygame.mixer.Sound(io.BytesIO(audio_data))
        sound.play()

        # Wait until the audio finishes playing
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)

        print("Audio played successfully.")
        
    except Exception as e:
        print(f"Error parsing response or playing audio: {e}")
        print("Raw response:", response.text[:100])

else:
    print(f"Error with TTS request, status code: {response.status_code}")
    print("Raw response:", response.text[:100])
