## Hamsa Voice Assistants

Voice-first examples that combine Hamsa STT/TTS APIs with OpenAI GPT for Arabic conversational flows, plus a Lahjati TTS demo. Files here are standalone scripts you can run individually.

### What’s inside
- `hamsa_realtime.py` – Async, continuous voice loop with VAD (webrtcvad) that records, sends to Hamsa STT, gets a GPT reply, and plays it via Hamsa TTS.
- `hamsa_workingcode.py` – Fixed-duration (no VAD) loop that records, sends to Hamsa STT, asks GPT, and plays back via Hamsa TTS; includes sync/async helpers for STT/TTS and recording.
- `hamsa.py` – Minimal file-based STT → canned reply → TTS playback example.
- `hamsa_stt.py` – Demonstrates converting WAV to Base64 and calling Hamsa STT.
- `hamsa_tts.py` – Demonstrates sending text to Hamsa TTS and playing the returned audio.
- `test_audio.py` – Records until silence using VAD and saves `mic_test.wav`.
- `lahjati.py` – Lahjati TTS example with in‑memory ffmpeg conversion and playback.

### Quick start
1) Install deps (from repo root):
```bash
pip install -r requirements.txt
```
2) Add API keys (recommended: environment variables):
```bash
set STT_API_KEY=your_hamsa_stt_key
set TTS_API_KEY=your_hamsa_tts_key
set OPENAI_API_KEY=your_openai_key
set LAHJATI_API_KEY=your_lahjati_key
```
3) Run an example:
- Realtime voice loop: `python hamsa_workingcode.py`
- Simple file-based flow: `python hamsa.py`
- STT only: `python hamsa_stt.py`
- TTS only: `python hamsa_tts.py`
- Lahjati TTS demo: `python lahjati.py`

### Notes
- Several scripts currently have keys hard-coded; replace them with env vars before sharing or deploying.
- Audio assumes 16 kHz mono PCM WAV; VAD frame sizes are tuned for low latency.
- pygame, sounddevice, ffmpeg (for Lahjati) must be available on your system.

