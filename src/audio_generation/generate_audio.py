import os
import time

from gtts import gTTS
from tqdm import tqdm
from TTS.api import TTS

def append_temp_to_final(temp_filename, final_filename):
    """
    Appends the contents of a temporary file to the final output file.
    :param temp_filename: The name of the temporary file.
    :param final_filename: The name of the final output file.
    :return: None
    """
    if os.path.exists(final_filename):
        with open(final_filename, 'ab') as f_out:
            with open(temp_filename, 'rb') as f_temp:
                f_out.write(f_temp.read())
    else:
        os.rename(temp_filename, final_filename)

def generate_audio_gtts(text, language='en', filename='output.mp3'):
    """
    Generates audio using gTTS library.
    :param text: The text to be converted into audio.
    :param language: The language of the text.
    :param filename: The name of the output audio file.
    :return: None
    """
    chunk_size = 200  # Adjusted chunk size
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    temp_filename = 'temp.mp3'

    try:
        with tqdm(total=len(chunks), desc='Generating Audio') as pbar:
            for chunk in chunks:
                tts = gTTS(text=chunk, lang=language, slow=False)
                tts.save(temp_filename)
                append_temp_to_final(temp_filename, filename)
                pbar.update(1)
                time.sleep(0.1)
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    print(f"Audio file generated: {filename}")

def generate_audio_mozilla_tts(text, model_name='tts_models/en/ljspeech/tacotron2-DCA', filename='output.wav'):
    """
    Generates audio using Mozilla TTS library.
    :param text: The text to be converted into audio.
    :param model_name: The name of the TTS model to use.
    :param filename: The name of the output audio file.
    :return: None
    """
    chunk_size = 200  # Adjusted chunk size
    min_chunk_length = 50  # Minimum length of a chunk to avoid errors
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    temp_filename = 'temp.wav'

    # Combine chunks if they are too short
    combined_chunks = []
    current_chunk = ""
    for chunk in chunks:
        if len(current_chunk) + len(chunk) < min_chunk_length:
            current_chunk += chunk
        else:
            if current_chunk:
                combined_chunks.append(current_chunk)
            current_chunk = chunk
    if current_chunk:
        combined_chunks.append(current_chunk)

    tts = TTS(model_name=model_name, progress_bar=False, gpu=False)

    try:
        with tqdm(total=len(combined_chunks), desc='Generating Audio') as pbar:
            for chunk in combined_chunks:
                tts.tts_to_file(text=chunk, file_path=temp_filename)
                append_temp_to_final(temp_filename, filename)
                pbar.update(1)
                time.sleep(0.1)
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    print(f"Audio file generated: {filename}")