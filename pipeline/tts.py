"""Turn cleaned text into speech using Google's Gemini TTS API."""

import base64
import os
import wave
import time 

from dotenv import load_dotenv
from google import genai
from pydub import AudioSegment

load_dotenv()
client = genai.Client()

MODEL = "gemini-3.1-flash-tts-preview"
VOICE = "Kore"  # easy to change later — one parameter, no rework needed


def _save_wave(path, pcm_bytes, channels=1, rate=24000, sample_width=2):
    """Gemini returns raw PCM audio, not a ready-made file — wrap it in a
    standard .wav header so it can be read back by anything, including
    pydub for the MP3 conversion below."""
    with wave.open(path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_bytes)


MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5


def _create_speech_with_retry(text):
    """Call the Gemini TTS API, retrying a few times on transient
    connection failures (observed in practice: 'Server disconnected
    without sending a response') before giving up."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return client.interactions.create(
                model=MODEL,
                input=text,
                response_format={"type": "audio"},
                generation_config={"speech_config": [{"voice": VOICE}]},
            )
        except Exception:
            if attempt == MAX_ATTEMPTS:
                raise
            time.sleep(RETRY_DELAY_SECONDS)


def synthesize(text, output_path):
    """Convert text to speech and save as an MP3 at output_path.

    Gemini's TTS models accept up to 32k tokens per request — far more
    than any single item we've seen — so unlike OpenAI's hard 4096-
    character limit, no chunking is needed here.
    """
    interaction = _create_speech_with_retry(text)
    pcm_bytes = base64.b64decode(interaction.output_audio.data)

    wav_path = f"{output_path}.wav"
    _save_wave(wav_path, pcm_bytes)
    AudioSegment.from_wav(wav_path).export(output_path, format="mp3")
    os.remove(wav_path)