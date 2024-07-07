import os
import shutil
import subprocess
import time

from pydub import AudioSegment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from src.html.generate_html import generate_html


def get_mp3_length(mp3_file):
    """
    Get the length of an MP3 file in seconds.

    :param mp3_file: The path to the MP3 file.
    :type mp3_file: str
    :return The length of the MP3 file in seconds.
    :rtype float
    """
    audio = AudioSegment.from_mp3(mp3_file)
    duration = len(audio) / 1000.0  # duration in seconds
    return duration


def reencode_mp3(input_file, output_file):
    """
    Re-encode an MP3 file to ensure proper format and integrity.

    :param input_file: The path to the input MP3 file.
    :type input_file: str
    :param output_file: The path to the output re-encoded MP3 file.
    :type output_file: str
    """
    try:
        # Load the MP3 file
        audio = AudioSegment.from_mp3(input_file)

        # Export the audio to a new MP3 file with the specified parameters
        audio.export(output_file, format="mp3", bitrate="192k")
        print(f"Re-encoded file saved as {output_file}")
    except Exception as e:
        print(f"An error occurred during re-encoding: {e}")


def get_mp3_length_v2(mp3_file, retries=3):
    """
    Get the length of an MP3 file in seconds, with re-encoding if necessary.

    :param mp3_file: The path to the MP3 file.
    :type mp3_file: str
    :param retries: Number of times to retry re-encoding if there are issues.
    :type retries: int
    :return: The length of the MP3 file in seconds.
    :rtype: float
    """
    attempt = 0
    if os.path.exists(mp3_file):
        temp_file = mp3_file

        while attempt <= retries:
            try:
                audio = AudioSegment.from_mp3(temp_file)
                duration = len(audio) / 1000.0  # duration in seconds
                return duration
            except Exception as e:
                print(f"Error: {e}")
                if attempt < retries:
                    print(f"Attempting re-encoding ({attempt + 1}/{retries})...")
                    new_temp_file = f"{mp3_file.rsplit('.', 1)[0]}_reencoded_{attempt + 1}.mp3"
                    try:
                        reencode_mp3(temp_file, new_temp_file)
                        temp_file = new_temp_file
                    except Exception as e:
                        print(f"An error occurred during re-encoding: {e}")
                        return None
                else:
                    print("Maximum re-encoding attempts reached. Failed to get the duration of the MP3 file.")
                    return None
            attempt += 1
    else:
        return 10


def copy_files_by_list(file_list, target_dir, prefix=""):
    """
    Copy files from the given file list to the target directory.

    :param file_list: A list of file names to be copied.
    :type file_list: list[str]
    :param target_dir: The target directory to which the files will be copied.
    :type target_dir: str
    :param prefix: An optional prefix to be added to the file paths.
    :type prefix: str
    :return None
    :rtype None
    """
    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    # Copy each file to the target directory
    for file_name in file_list:
        # Define the full path of the source file
        file_path = os.path.join(os.getcwd(), prefix, file_name)

        # Check if the file exists
        if os.path.exists(file_path):
            # Define the target path
            target_path = os.path.join(target_dir, file_name)

            # Copy the file
            shutil.copy(file_path, target_path)
            print(f"Copied {file_path} to {target_path}")
        else:
            print(f"File {file_name} does not exist in the current directory")


def record_mp4_task(index, row, output_dir, version, extension):
    """
    :param index: The unique identifier for the task.
    :param row: The row of data containing the task details.
    :param output_dir: The directory where the output files will be saved.
    :return None

    This method is used to record a task as an MP4 video. It takes four parameters: `index`, `row`, `template`,
    and `output_dir`. The `index` parameter is the unique identifier for the task. It is used to generate the
    filenames for the HTML, MP4, MP3, and with-audio MP4 files. The `row` parameter is the row of data containing the
    task details. It is used to populate the template with the appropriate values. The `template` parameter is the
    template used to render the HTML content. It should be a valid template object that supports rendering with the
    `render` method. The `output_dir` parameter is the directory where the output files will be saved. The HTML, MP4,
    MP3, and with-audio MP4 files will be created in this directory.

    This method performs the following steps: 1. Renders the HTML content using the template and the values from the
    `row` parameter. 2. Saves the rendered HTML content to a file with a filename generated based on the `index`
    parameter. 3. Calls the `record_mp4` function to convert the HTML file to an MP4 video, using the provided
    `html_file` and `mp4_file` filenames and the duration of the corresponding MP3 file. 4. Checks if the
    corresponding MP3 file exists. 5. If the MP3 file exists, calls the `combine_video_audio` function to combine the
    MP4 video and MP3 audio files, using the provided `mp4_file` and `mp3_file` filenames, and saves the result to a
    new file with a filename generated based on the `index` parameter.
    """
    html_file = os.path.join(output_dir, f'comment_{index}.html')
    mp4_file = os.path.join(output_dir, f'comment_{index}.{extension}')
    mp3_file = os.path.join(output_dir, f'comment_{index}.mp3')

    generate_html(row, html_file, version)

    print(f"Processing {html_file} to {mp4_file}")
    record_html(html_file, mp4_file, get_mp3_length_v2(mp3_file))


def get_window_id(window_name):
    """
    Get the ID of a window with the given name.

    :param window_name: The name of the window to search for.
    :type window_name: str
    :return The ID of the window, or None if the window is not found.
    :rtype str or None
    """
    try:
        result = subprocess.run(['xdotool', 'search', '--name', window_name], stdout=subprocess.PIPE)
        window_ids = result.stdout.decode().strip().split()
        if window_ids:
            return window_ids[0]
        else:
            print("Window not found.")
            return None
    except Exception as e:
        print(f"Error finding window ID: {e}")
        return None


def get_window_geometry(window_id):
    """
    :param window_id: The ID of the window
    :return The x and y position, width, and height of the window as integers
    """
    result = subprocess.run(['xdotool', 'getwindowgeometry', window_id], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    position = output.split("Position: ")[1].split(" (")[0]
    size = output.split("Geometry: ")[1].strip()
    x, y = position.split(",")
    width, height = size.split("x")
    return int(x), int(y), int(width), int(height)


def record_html(path, output, duration, framerate=120):
    """
    :param path: The path to the HTML file or URL that needs to be recorded.
    :param output: The output file path where the recorded video/audio should be saved.
    :param duration: The duration of the recording in seconds.
    :param framerate: The framerate of the recording.
    :return None

    This method records a video or audio of the specified HTML page or URL using the Chrome browser and FFmpeg.
    """
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    # Ensure path is a valid URL or file path
    if not path.startswith(('http://', 'https://')):
        path = f"file://{os.path.abspath(path)}?duration={duration * 1000}"

    driver.get(path)

    # Inject CSS to hide the cursor
    driver.execute_script("""
        const style = document.createElement('style');
        style.innerHTML = '* { cursor: none !important; }';
        document.head.appendChild(style);
    """)

    driver.execute_script("document.title = 'Sample HTML';")
    time.sleep(1)  # Wait for the page to load

    window_id = get_window_id('Sample HTML')
    if not window_id:
        print("Could not find window ID.")
        driver.quit()
        return

    x, y, width, height = get_window_geometry(window_id)
    print(f"Window geometry - X: {x}, Y: {y}, Width: {width}, Height: {height}")

    # Adjust coordinates if necessary
    x = max(0, x)
    y = max(0, y)

    # Determine file extension and set appropriate FFmpeg command
    file_extension = os.path.splitext(output)[1].lower()
    if file_extension in ['.mp4', '.mkv']:
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-f', 'x11grab', '-video_size', f'{width}x{height}', '-i', f':0.0+{x},{y}',
            '-codec:v', 'libx264', '-r', str(framerate), '-t', str(duration + 1), output
        ]
    else:
        print(f"Unsupported file extension: {file_extension}")
        driver.quit()
        return

    # Start FFmpeg to record
    ffmpeg = subprocess.Popen(ffmpeg_cmd)

    try:
        # Wait until the body element has the data-rendering-over attribute
        WebDriverWait(driver, duration + 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body[data-rendering-over]"))
        )
        print("Rendering is over, stopping the recording and closing the browser.")
    except Exception as e:
        print(f"Error or timeout waiting for attribute: {e}")
    finally:
        ffmpeg.terminate()
        driver.quit()
        ffmpeg.wait()
