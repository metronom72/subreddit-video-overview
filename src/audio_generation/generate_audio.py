import json
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
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def append_temp_to_final(temp_filename, final_filename):
    with open(temp_filename, 'rb') as temp_file:
        with open(final_filename, 'ab') as final_file:
            final_file.write(temp_file.read())


def split_text_into_phrases(text, max_length, chunk_size):
    split_by_max_length = textwrap.wrap(text, max_length)
    split_into_chunks = [textwrap.wrap(chunk, chunk_size) for chunk in split_by_max_length]
    split_into_chunks = [chunk for sublist in split_into_chunks for chunk in sublist]
    return split_into_chunks


def generate_audio_gtts(text, output_file='output.mp3', language='en', metadata=None):
    chunk_size = 200
    chunks = split_text_into_phrases(text, 50, chunk_size)
    temp_filename = 'temp.mp3'
    ensure_directory_exists(output_file)

    start_time = time.time()
    chunk_times = []

    try:
        with tqdm(total=len(chunks), desc='Generating Audio with gTTS') as pbar:
            for chunk in chunks:
                chunk_start_time = time.time()
                tts = gTTS(text=chunk, lang=language, slow=False)
                tts.save(temp_filename)
                append_temp_to_final(temp_filename, output_file)
                chunk_end_time = time.time()
                chunk_times.append(chunk_end_time - chunk_start_time)
                pbar.update(1)
                print(f"Chunk generated in {chunk_end_time - chunk_start_time:.2f} seconds")
                time.sleep(0.1)
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    total_time = time.time() - start_time
    print(f"Audio file generated: {output_file}")
    print(f"Total generation time: {total_time:.2f} seconds")
    print(f"Chunk size: {chunk_size}")
    print(f"Input text: {text}")
    print(f"Language: {language}")

    metadata = metadata or {}
    metadata.update({
        'total_generation_time': total_time,
        'chunk_times': chunk_times,
        'chunk_size': chunk_size,
        'input_text': text,
        'language': language
    })

    metadata_file = os.path.splitext(output_file)[0] + '_audio_generation_metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)


def preprocess_text(text):
    text = re.sub(r'[^\w\s,.!?]', '', text)
    processed_text = re.sub(r'(?<=[.!?])(?=\S)', ' ', text)
    return processed_text


def split_text_into_chunks(text, chunk_size=200):
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
    y, sr = librosa.load(file_path, sr=None)
    silent_threshold = 20
    silent_segments = librosa.effects.split(y, top_db=silent_threshold)
    silent_durations = [(end - start) / sr for start, end in silent_segments]

    if any(duration > 2 for duration in silent_durations):
        print("Detected long silent segments in the audio.")
        return False

    rms = librosa.feature.rms(y=y)
    rms_diff = np.diff(rms[0])
    if np.any(rms_diff == 0):
        print("Detected possible repetitions in the audio.")
        return False

    return True


def generate_audio_chunk(tts, chunk, temp_file):
    for attempt in range(4):
        tts.tts_to_file(text=chunk, file_path=temp_file)
        return True


def generate_audio_chunk(tts, text_chunk, output_file, max_retries=10):
    retry_count = 0
    while retry_count < max_retries:
        chunk_start_time = time.time()
        try:
            tts.tts_to_file(text=text_chunk, file_path=output_file)
            chunk_end_time = time.time()
            if chunk_end_time - chunk_start_time > 60:
                raise Exception("Chunk generation took too long")
            return True, chunk_end_time - chunk_start_time
        except Exception as e:
            retry_count += 1
            print(f"Error generating audio chunk: {e}. Retrying {retry_count}/{max_retries}")
    return False, 0


def generate_audio_mozilla_tts(text, output_file='output.mp3', model_name='tts_models/en/ljspeech/tacotron2-DDC',
                               metadata=None):
    ensure_directory_exists(output_file)
    processed_text = preprocess_text(text)
    text_chunks = split_text_into_chunks(processed_text)
    tts = TTS(model_name=model_name, progress_bar=True, gpu=False)

    start_time = time.time()
    chunk_times = []
    temp_files = []

    for i, chunk in enumerate(text_chunks):
        temp_file = f"{os.path.splitext(output_file)[0]}_part_{i}.wav"
        success, chunk_time = generate_audio_chunk(tts, chunk, temp_file)
        if success:
            chunk_times.append(chunk_time)
            temp_files.append(temp_file)
            print(f"Chunk {i + 1}/{len(text_chunks)} generated in {chunk_time:.2f} seconds")
        else:
            print(f"Failed to generate audio for chunk: {chunk}")
            return

    combined = AudioSegment.empty()
    for temp_file in temp_files:
        combined += AudioSegment.from_wav(temp_file)
        os.remove(temp_file)

    combined.export(output_file, format="mp3")

    total_time = time.time() - start_time
    print(f"Audio file generated: {output_file}")
    print(f"Total generation time: {total_time:.2f} seconds")
    print(f"Chunk size: 200")
    print(f"Input text: {text}")
    print(f"Model name: {model_name}")

    metadata = metadata or {}
    metadata.update({
        'total_generation_time': total_time,
        'chunk_times': chunk_times,
        'chunk_size': 200,
        'input_text': text,
        'model_name': model_name
    })

    metadata_file = os.path.splitext(output_file)[0] + '_audio_generation_metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)
