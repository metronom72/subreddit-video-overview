import os
import time

from gtts import gTTS
from tqdm import tqdm


def generate_audio(text, language='en', filename='output.mp3'):
    # Split the text into chunks for progress indication
    chunk_size = 100  # You can adjust the chunk size as needed
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Create a progress bar
    with tqdm(total=len(chunks), desc='Generating Audio') as pbar:
        # Create gTTS object for each chunk
        for chunk in chunks:
            tts = gTTS(text=chunk, lang=language, slow=False)
            # Save each chunk to a temporary file
            temp_filename = 'temp.mp3'
            tts.save(temp_filename)
            # Append the temporary file to the final output file
            if os.path.exists(filename):
                os.system(f"cat {temp_filename} >> {filename}")
            else:
                os.rename(temp_filename, filename)
            pbar.update(1)
            # Sleep to simulate processing time (optional)
            time.sleep(0.1)

    print(f'Audio content written to file "{filename}"')
