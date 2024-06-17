import os
import time

from gtts import gTTS
from tqdm import tqdm


def generate_audio(text, language='en', filename='output.mp3'):
    """
    :param text: The text to be converted into audio.
    :param language: The language of the text (default is 'en' for English).
    :param filename: The name of the output audio file (default is 'output.mp3').
    :return: None

    This method takes a text input and generates an audio file using the gTTS library. It divides the input text into chunks for processing and creates a progress bar to indicate the progress of audio generation. Each chunk is converted to audio and saved to a temporary file. If the output file already exists, each temporary file is appended to it, otherwise the temporary file is renamed to the output file. The method uses the `time` module to simulate processing time for each chunk (0.1 seconds). Once the audio generation is complete, the method prints the name of the output file.
    """
    chunk_size = 100  # You can adjust the chunk size as needed
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    temp_filename = 'temp.mp3'

    try:
        with tqdm(total=len(chunks), desc='Generating Audio') as pbar:
            for chunk in chunks:
                tts = gTTS(text=chunk, lang=language, slow=False)
                tts.save(temp_filename)

                if os.path.exists(filename):
                    with open(filename, 'ab') as f_out:
                        with open(temp_filename, 'rb') as f_temp:
                            f_out.write(f_temp.read())
                else:
                    os.rename(temp_filename, filename)

                pbar.update(1)
                time.sleep(0.1)
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            