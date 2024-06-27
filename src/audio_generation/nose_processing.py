from pydub import AudioSegment
import noisereduce as nr
import numpy as np


def load_audio(file_path):
    """
    Load an audio file and return as an AudioSegment.
    """
    return AudioSegment.from_file(file_path)


def save_audio(audio_segment, file_path):
    """
    Save an AudioSegment to a file.
    """
    audio_segment.export(file_path, format="wav")


def reduce_noise(audio_segment):
    """
    Reduce background noise in an AudioSegment.
    """
    # Convert AudioSegment to numpy array
    samples = np.array(audio_segment.get_array_of_samples())

    # Perform noise reduction
    reduced_noise_samples = nr.reduce_noise(y=samples, sr=audio_segment.frame_rate)

    # Convert numpy array back to AudioSegment
    reduced_noise_audio_segment = audio_segment._spawn(reduced_noise_samples.tobytes())

    return reduced_noise_audio_segment


def remove_background_noise(input_file, output_file):
    """
    Load an audio file, reduce background noise, and save the result.
    """
    audio = load_audio(input_file)
    reduced_noise_audio = reduce_noise(audio)
    save_audio(reduced_noise_audio, output_file)
    print(f"Background noise removed. Cleaned audio saved as: {output_file}")
