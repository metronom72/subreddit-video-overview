import os
import shutil
import tempfile
import unittest

from pydub import AudioSegment

from src.video.record_html import get_mp3_length, copy_files_by_list


class TestRecordHtml(unittest.TestCase):
    def setUp(self):
        self.test_audio_file = os.path.join(tempfile.gettempdir(), 'test.mp3')

        # Create a mp3 file with 5 seconds of silence
        silence = AudioSegment.silent(duration=5000)
        silence.export(self.test_audio_file, format="mp3").close()  # Close the file after exporting

        self.test_dir = 'test_dir'
        self.test_files = ['test1.txt', 'test2.txt']
        self.prefix = 'src'
        os.makedirs(self.test_dir, exist_ok=True)
        for file in self.test_files:
            with open(os.path.join(self.test_dir, file), 'w') as f:
                f.write('Test Data')
        self.target_dir = 'target_dir'

    def tearDown(self):
        os.remove(self.test_audio_file)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        if os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir, ignore_errors=True)

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

    def test_copy_files_by_list(self):
        copy_files_by_list(self.test_files, self.target_dir, self.prefix)
        self.assertTrue(all(os.path.exists(os.path.join(self.target_dir, self.prefix, f)) for f in self.test_files))

    def test_copy_files_by_list_with_nonexistent_files(self):
        copy_files_by_list(['nonexistent.txt'], self.target_dir, self.prefix)
        self.assertFalse(os.path.exists(os.path.join(self.target_dir, self.prefix, 'nonexistent.txt')))

    def test_copy_files_by_list_with_empty_list(self):
        copy_files_by_list([], self.target_dir, self.prefix)
        self.assertFalse(any(os.path.exists(os.path.join(self.target_dir, self.prefix, f)) for f in self.test_files))


if __name__ == "__main__":
    unittest.main()
