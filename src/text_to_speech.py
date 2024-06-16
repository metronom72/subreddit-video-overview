from pathlib import Path
from openai import OpenAI, OpenAIError, RateLimitError
import time

# Set your OpenAI API key
api_key = "sk-proj-yvF2B2A1DIRBYLI2UN1DT3BlbkFJhraHCrGakMkL5ZDQTsQY"

# Initialize OpenAI client with API key
client = OpenAI(api_key=api_key)


def text_to_mp3(text, file):
    """
    Convert text to MP3 audio file.

    :param text: The text to convert to speech.
    :type text: str
    :param file: The file path to save the MP3 audio.
    :type file: str
    :return: None
    :rtype: None
    """
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            # Generate speech
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )

            # Save speech to file
            response.stream_to_file(file)
            return;
        except RateLimitError as e:
            retries += 1
            print(f"Rate limit exceeded. Retry {retries}/{max_retries}. Waiting before retrying...")
            print(e)
            time.sleep(60)  # Wait for a minute before retrying
        except OpenAIError as e:
            print("An error occurred:", e)
            break
