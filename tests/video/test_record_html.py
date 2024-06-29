import unittest
from src.video.record_html import get_mp3_length
from pydub import AudioSegment
import os
import tempfile

class TestMP3Length(unittest.TestCase):

    def setUp(self):
        self.test_audio_file = os.path.join(tempfile.gettempdir(), 'test.mp3')

        # Create a mp3 file with 5 seconds of silence
        silence = AudioSegment.silent(duration=5000)
        silence.export(self.test_audio_file, format="mp3")

    def tearDown(self):
        os.remove(self.test_audio_file)

    def test_get_audio_length_formatter(self):
        duration = get_mp3_length(self.test_audio_file)
        self.assertEqual(duration, 5.0)

    def test_get_audio_length_with_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            duration = get_mp3_length("not_exist.mp3")

    def test_get_audio_length_with_non_mp3_file(self):
        non_mp3_file = os.path.join(tempfile.gettempdir(), 'test.txt')
        with open(non_mp3_file, 'w') as f:
            f.write("this is a text file")
        with self.assertRaises(Exception):
            get_mp3_length(non_mp3_file)
        os.remove(non_mp3_file)


if __name__ == "__main__":
    unittest.main()