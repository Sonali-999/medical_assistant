#step1a:setup text to speech TTS model (gTTS )
import os
from gtts import gTTS

def text_to_speech_with_gtts_old(input_text, output_filepath): 
    language = 'en'  # Specify the language for TTS

    audioobj=gTTS(
        text=input_text, 
        lang=language, 
        slow=False
        )  # Create a gTTS object
    audioobj.save(output_filepath)  # Save the audio file
    print(f"Audio saved at {output_filepath}")
    
input_text="Hi this is gTTS"


#step2: Use model for Text output to voice
import subprocess
import platform

# from elevenlabs import generate, play, save, set_api_key
import platform
import subprocess
import os

def text_to_speech_with_gtts(input_text, output_filepath): 
    language = 'en'  # Specify the language for TTS

    audioobj=gTTS(
        text=input_text, 
        lang=language, 
        slow=False
        )  # Create a gTTS object
    try:
        audioobj.save(output_filepath)  # Save the audio file
    except PermissionError:
        print(f"Permission denied when trying to save {output_filepath}. Please close any program using this file or check permissions.")
        return

    os_name = platform.system()
    try:
        if os_name == 'Windows':
            # Use Windows built-in 'start' command to play audio asynchronously
            subprocess.run(['cmd', '/c', 'start', '', output_filepath], check=True)
        elif os_name == 'Darwin':  # macOS
            subprocess.run(['afplay', output_filepath], check=True)
        elif os_name == "Linux": # Linux and other 
            subprocess.run(['aplay', output_filepath], check=True)
        else:
            print(f"Unsupported OS: {os_name}. Cannot play audio automatically.")
    except subprocess.CalledProcessError as e:
        print(f"Error playing audio: {e}")
    except Exception as e:
        print(f"Unexpected error playing audio: {e}")

    print(f"Audio saved at {output_filepath}")


# Example usage for gTTS with auto play
input_text_gtts = "Hi this is autoplay testing with gTTS"
text_to_speech_with_gtts(input_text_gtts, "gtt_testing_part1.mp3")
