
"""
### Description:

This Python script continuously records audio using the `sounddevice` library. It applies WebRTC-based Voice Activity Detection (VAD) to detect when the user is speaking. The recording stops after detecting a predefined amount of silence, and the captured audio is saved as a WAV file.

### Components:

1. **Configuration**:
    - `samplerate`: Defines the audio sample rate (16 kHz).
    - `frame_ms`: Sets the frame size in milliseconds for the VAD. Smaller frame sizes result in quicker speech detection.
    - `silence_ms`: Determines how long the system waits after silence is detected before stopping the recording (set to approximately 1 second).
    - `vad`: Initializes WebRTC VAD with a sensitivity level of 1 (less aggressive detection for faster responses).

2. **PCM to WAV Conversion**:
    - The `pcm_frames_to_wav_bytes` function converts the recorded PCM audio frames into a WAV format and stores the audio in memory using `io.BytesIO`.

3. **Audio Recording**:
    - The `record_until_silence` function listens to the microphone input using `sounddevice.InputStream`.
    - It uses the WebRTC VAD to detect speech. When the VAD detects no speech (silence), it increments a counter. If silence exceeds the threshold (`silence_ms`), the recording stops.
    - The audio frames are combined, converted to WAV, and returned as a byte array.

4. **Callback Function**:
    - The callback function processes each audio frame, checks if the frame contains speech using VAD, and appends the frames to a list.
    - If continuous silence is detected, the stream is stopped, and the audio is processed.

5. **File Saving**:
    - The recorded audio is saved as `mic_test.wav` after the silence threshold is reached.

6. **Usage**:
    - This function listens until silence is detected, then saves the audio file, allowing the user to record short segments of speech in real-time.

### Workflow:
1. The system starts recording as soon as the user begins speaking.
2. It continuously records and checks if speech is detected using WebRTC VAD.
3. Once the system detects silence for the specified threshold (`silence_ms`), the recording stops.
4. The recorded audio is saved as a WAV file (`mic_test.wav`).
5. The WAV data is returned in memory for further processing or saving.

### Potential Use Cases:
- Real-time speech recognition or transcription.
- Voice-controlled applications that need to respond to short bursts of speech.
- Audio recording with automatic stop after a user finishes speaking.
"""


import sounddevice as sd
import wave
import webrtcvad
import numpy as np
import io

samplerate = 16000
frame_ms = 10          # Frame size in ms (smaller frame size for quicker detection)
silence_ms = 500      # Stop after ~1s of silence
vad = webrtcvad.Vad(1)  # Less aggressive for faster response (1 or 2 should work)

# Function to convert PCM frames to WAV format in memory
def pcm_frames_to_wav_bytes(pcm_frames: np.ndarray, samplerate: int = 16000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(samplerate)
        wf.writeframes(pcm_frames.tobytes())
    buf.seek(0)
    return buf.read()

# Function to record audio until silence is detected
def record_until_silence():
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

        if continuous_silence_ms >= silence_ms and len(audio_frames) > int(silence_ms / frame_ms):
            raise sd.CallbackStop()  # Stop stream if silence threshold is exceeded

    try:
        # Start the recording stream with specified parameters
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16',
                            blocksize=frame_size, callback=callback):
            sd.sleep(10000)  # Safety cap to ensure the stream stops after a max duration (10s)

    except sd.CallbackStop:
        pass  # The stream stopped due to silence detection

    # Combine all frames into a single audio array
    audio = np.concatenate(audio_frames, axis=0)
    
    # Convert audio frames to WAV format in memory
    wav_bytes = pcm_frames_to_wav_bytes(audio, samplerate)

    # For testing, you can optionally save the file
    with open("mic_test.wav", "wb") as f:
        f.write(wav_bytes)

    print("✅ Saved mic_test.wav after silence")
    return wav_bytes  # Return the WAV bytes directly

# Run the function
record_until_silence()
