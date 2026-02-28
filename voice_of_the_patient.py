#step1:setup Audio recorder(ffmpeg & poraudio)
#ffmpeg, portaudio, pydub, speech_recognition
import logging
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which

AudioSegment.converter = which("ffmpeg") or r"C:\Users\sonal\OneDrive\Documents\srip_proj\ffmpeg\bin\ffmpeg.exe"

from io import BytesIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def record_audio(file_path,timeout=20, phrase_time_limit=None):
    """
    Simplified function to record audio from the microphone and save it to an MP3 file.

    Args:
        file_path (str): Path to save the recorded audio file.
        timeout (int): Maximum time to wait for speech input.
        phrase_time_limit (int, optional): Maximum length of a phrase to record.
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()


    try:
        with microphone as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source,duration=1)
            logging.info("start speaking now...")

            # Record audio 
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete. Processing audio...")

            #convert recorded audio to MP3 format file
            wave_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wave_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")

            logging.info(f"Audio saved to {file_path}")

    except Exception as e:
        logging.error(f"An error occurred while recording audio: {e}")
audio_filepath = "patient_voice_again.mp3"

record_audio(file_path=audio_filepath)
#step2:setup speech to text SST model for transcription
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def transcribe_audio_with_groq(stt_model, audio_file_path, GROQ_API_KEY):
    client= Groq(api_key=GROQ_API_KEY)
    stt_model="whisper-large-v3-turbo"
    audio_file=open(audio_filepath, "rb")
    transcription=client.audio.transcriptions.create(
        model=stt_model,
        file=audio_file,
        language="en"
    )
    return transcription.text