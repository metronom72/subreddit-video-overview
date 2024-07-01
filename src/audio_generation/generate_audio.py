import os
import re
import textwrap
import time

import librosa
import numpy as np
from TTS.api import TTS
from gtts import gTTS
from pydub import AudioSegment
from tqdm import tqdm


def ensure_directory_exists(file_path):
    """
    Ensures that the directory for the given file path exists.
    Creates the directory if it doesn't exist.
    :param file_path: The file path to check.
    :return None
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def append_temp_to_final(temp_filename, final_filename):
    """
    Appends the content of the temporary file to the final file.
    :param temp_filename: The temporary file name.
    :param final_filename: The final file name.
    :return None
    """
    with open(temp_filename, 'rb') as temp_file:
        with open(final_filename, 'ab') as final_file:
            final_file.write(temp_file.read())


def split_text_into_phrases(text, max_length, chunk_size):
    # First split the text by the max_length
    split_by_max_length = textwrap.wrap(text, max_length)

    # Then, split each chunk further by the chunk_size
    split_into_chunks = [textwrap.wrap(chunk, chunk_size) for chunk in split_by_max_length]

    # Flattening the list of lists
    split_into_chunks = [chunk for sublist in split_into_chunks for chunk in sublist]

    return split_into_chunks


def generate_audio_gtts(text, output_file='output.mp3', language='en'):
    """
    Generates audio using gTTS library.
    :param text: The text to be converted into audio.
    :param output_file: The name of the output audio file.
    :param language: The language of the text.
    :return None
    """
    chunk_size = 200  # Adjusted chunk size
    chunks = split_text_into_phrases(text, 50, chunk_size)
    temp_filename = 'temp.mp3'

    ensure_directory_exists(output_file)

    try:
        with tqdm(total=len(chunks), desc='Generating Audio with gTTS') as pbar:
            for chunk in chunks:
                tts = gTTS(text=chunk, lang=language, slow=False)
                tts.save(temp_filename)
                append_temp_to_final(temp_filename, output_file)
                pbar.update(1)
                time.sleep(0.1)
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    print(f"Audio file generated: {output_file}")


def preprocess_text(text):
    """
    Preprocess the text to ensure smooth transitions between sentences and remove unsupported characters.
    :param text: The text to be converted into audio.
    :return Preprocessed text.
    """
    # Remove unsupported characters
    text = re.sub(r'[^\w\s,.!?]', '', text)
    # Insert a pause between sentences by adding a period followed by a space
    processed_text = re.sub(r'(?<=[.!?])(?=\S)', ' ', text)
    return processed_text


def split_text_into_chunks(text, chunk_size=200):
    """
    Splits text into smaller chunks to avoid decoder step limit.
    :param text: The text to be converted into audio.
    :param chunk_size: The maximum number of characters in each chunk.
    :return A list of text chunks.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += len(word) + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def check_audio_quality(file_path):
    """
    Check the quality of the generated audio file.
    :param file_path: The path to the audio file.
    :return True if the quality is acceptable, False otherwise.
    """
    # Load audio file
    y, sr = librosa.load(file_path, sr=None)

    # Check for long silent segments
    silent_threshold = 20  # Threshold in dB
    silent_segments = librosa.effects.split(y, top_db=silent_threshold)

    # Calculate durations of silent segments
    silent_durations = [(end - start) / sr for start, end in silent_segments]

    # Check if there are long silent segments
    if any(duration > 2 for duration in silent_durations):  # Adjust threshold as needed
        print("Detected long silent segments in the audio.")
        return False

    # Check for repetitions (basic check using RMS energy)
    rms = librosa.feature.rms(y=y)
    rms_diff = np.diff(rms[0])
    if np.any(rms_diff == 0):  # Adjust threshold as needed
        print("Detected possible repetitions in the audio.")
        return False

    return True


def generate_audio_chunk(tts, chunk, temp_file):
    """
    Generate audio for a text chunk and save it to a temporary file.
    :param tts: The TTS object.
    :param chunk: The text chunk.
    :param temp_file: The temporary file path.
    :return True if the chunk is generated successfully, False otherwise.
    """
    for attempt in range(4):  # Retry up to 4 times
        tts.tts_to_file(text=chunk, file_path=temp_file)
        return True
    #     if check_audio_quality(temp_file):
    #         return True
    #     print(f"Retrying chunk generation (Attempt {attempt + 1}) for: {chunk}")
    # return False


def generate_audio_mozilla_tts(text, output_file='output.wav', model_name='tts_models/en/ljspeech/tacotron2-DDC'):
    """
    Generates audio using Mozilla TTS library with a progress bar.
    :param text: The text to be converted into audio.
    :param output_file: The name of the output audio file.
    :param model_name: The name of the TTS model to use.
    :return None
    """
    ensure_directory_exists(output_file)

    # Preprocess text for smoother transitions and to remove unsupported characters
    processed_text = preprocess_text(text)

    # Split text into smaller chunks
    text_chunks = split_text_into_chunks(processed_text)

    # Initialize TTS with progress bar enabled
    tts = TTS(model_name=model_name, progress_bar=True, gpu=False)

    # Generate audio for each chunk and save to temporary files
    temp_files = []
    for i, chunk in enumerate(text_chunks):
        temp_file = f"{os.path.splitext(output_file)[0]}_part_{i}.wav"
        if generate_audio_chunk(tts, chunk, temp_file):
            temp_files.append(temp_file)
        else:
            print(f"Failed to generate audio for chunk: {chunk}")
            return  # Exit if a chunk fails after 4 attempts

    # Concatenate temporary audio files into the final output file
    combined = AudioSegment.empty()
    for temp_file in temp_files:
        combined += AudioSegment.from_wav(temp_file)
        os.remove(temp_file)

    combined.export(output_file, format="wav")

    print(f"Audio file generated: {output_file}")
