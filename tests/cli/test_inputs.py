import os
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

import pandas as pd

from src.cli import inputs  # Make sure to import your module correctly


class TestInputs(unittest.TestCase):
    def setUp(self):
        self.default_output_directory = "output_"
        self.test_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.test_dir, "folder1"))  # Setup a test folder inside test directory
        os.mkdir(os.path.join(self.test_dir, "folder2"))  # Setup a second test folder inside test directory

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        for item in os.scandir():
            if item.is_dir() and item.name.startswith(self.default_output_directory):
                os.rmdir(item)

    def create_test_files(self, filenames):
        for filename in filenames:
            open(os.path.join(self.test_dir, filename), 'a').close()

    def test_list_csv_files_empty_dir(self):
        self.assertEqual(inputs.list_csv_files(self.test_dir), [])

    def test_list_csv_files_one_csv(self):
        filenames = ['test.csv']
        self.create_test_files(filenames)
        self.assertEqual(inputs.list_csv_files(self.test_dir), filenames)

    def test_list_csv_files_multiple_csvs(self):
        filenames = ['b.csv', 'a.csv', 'c.csv']
        self.create_test_files(filenames)
        self.assertEqual(inputs.list_csv_files(self.test_dir), sorted(filenames))

    def test_list_csv_files_ignore_non_csv(self):
        filenames = ['test.csv', 'ignore.txt']
        self.create_test_files(filenames)
        self.assertEqual(inputs.list_csv_files(self.test_dir), ['test.csv'])

    def test_list_folders(self):
        """Test that list_folders function returns list of folders in correct order."""
        expected_value = ['folder1', 'folder2']
        returned_value = inputs.list_folders(self.test_dir)
        self.assertListEqual(returned_value, expected_value)

    @patch('builtins.input', side_effect=['https://reddit.com/post', '5', '1'])
    @patch('src.cli.inputs.fetch_subreddit')
    @patch('pandas.read_csv')
    def test_fetch_comments(self, mock_read_csv, mock_fetch_subreddit, mock_input):
        # Create test CSV files
        filenames = ['sample1.csv', 'sample2.csv']
        self.create_test_files(filenames)

        with patch('src.cli.inputs.list_csv_files', return_value=filenames):
            inputs.fetch_comments()
            mock_input.assert_any_call('Enter the Reddit post URL (required): ')
            mock_input.assert_any_call('Enter the number of top comments to fetch (required): ')
            mock_input.assert_any_call('Enter the number corresponding to the CSV file (1-2): ')
            mock_fetch_subreddit.assert_called_once_with('https://reddit.com/post', 5)
            mock_read_csv.assert_called_once_with(os.path.join('samples', 'sample1.csv'))  # Use os.path.join directly

    @patch('builtins.input', side_effect=['https://reddit.com/post', '5'])
    @patch('src.cli.inputs.fetch_subreddit')
    @patch('pandas.read_csv')
    def test_fetch_comments_no_csv(self, mock_read_csv, mock_fetch_subreddit, mock_input):
        with patch('src.cli.inputs.list_csv_files', return_value=[]):
            result = inputs.fetch_comments()
            mock_input.assert_any_call('Enter the Reddit post URL (required): ')
            mock_input.assert_any_call('Enter the number of top comments to fetch (required): ')
            mock_fetch_subreddit.assert_called_once_with('https://reddit.com/post', 5)
            self.assertIsNone(result)
            mock_read_csv.assert_not_called()

    @patch('os.path.exists')
    @patch('src.cli.inputs.combine_video_audio')
    def test_combine_video_audio_task_mp3_exists(self, mock_combine_video_audio, mock_os_path_exists):
        mock_os_path_exists.return_value = True
        index = 1
        row = []
        output_dir = '/test/output_dir'

        inputs.combine_video_audio_task(index, row, output_dir)

        mp3_file = os.path.join(output_dir, f'comment_{index}.mp3')
        mp4_file = os.path.join(output_dir, f'comment_{index}.mp4')
        with_audio_mp4_file = os.path.join(output_dir, f'comment_{index}_with_audio.mp4')

        mock_combine_video_audio.assert_called_once_with(mp4_file, mp3_file, with_audio_mp4_file)

    @patch('os.path.exists')
    @patch('src.cli.inputs.combine_video_audio')
    def test_combine_video_audio_task_mp3_not_exists(self, mock_combine_video_audio, mock_os_path_exists):
        mock_os_path_exists.return_value = False
        index = 1
        row = []
        output_dir = '/test/output_dir'

        inputs.combine_video_audio_task(index, row, output_dir)

        mock_combine_video_audio.assert_not_called()

    @patch('src.cli.inputs.list_folders')
    @patch('builtins.input', side_effect=['1', '2', '3'])
    @patch('src.cli.inputs.print')
    def test_select_version(self, mock_print, mock_input, mock_list_folders):
        # Test no versions found
        mock_list_folders.return_value = []
        self.assertIsNone(inputs.select_version('templates_dir'))

        # Test for single version in directory
        mock_list_folders.return_value = ['1']
        self.assertEqual(inputs.select_version('templates_dir'), '1')

        # Test for invalid version selection
        mock_list_folders.return_value = []
        self.assertIsNone(inputs.select_version('templates_dir'))

        # Test for multiple versions in directory
        mock_list_folders.return_value = ['1', '2']
        self.assertEqual(inputs.select_version('templates_dir'), '2')

    @patch('src.cli.inputs.generate_audio_gtts')
    def test_generate_audio_files_gtts(self, mock_generate_audio_gtts):
        data = pd.DataFrame({'comment': ['test comment']})
        tts_library = 'gtts'
        output_dir = 'test_dir'

        inputs.generate_audio_files(data, tts_library, output_dir)

        mock_generate_audio_gtts.assert_called_once_with('test comment', 'en', 'test_dir/comment_0.mp3')

    @patch('src.cli.inputs.generate_audio_mozilla_tts')
    def test_generate_audio_files_mozilla_tts(self, mock_generate_audio_mozilla_tts):
        data = pd.DataFrame({'comment': ['test comment']})
        tts_library = 'mozilla_tts'
        output_dir = 'test_dir'

        inputs.generate_audio_files(data, tts_library, output_dir)

        mock_generate_audio_mozilla_tts.assert_called_once_with('test comment', 'test_dir/comment_0.mp3')

    @patch('src.cli.inputs.record_mp4_task')
    def test_record_videos_with_valid_data(self, mock):
        data = pd.DataFrame({"column1": [1, 2, 3], "column2": ['a', 'b', 'c']})
        version = 1.0
        output_dir = '/dummy/path'

        inputs.record_videos(data, version, output_dir)

        self.assertEqual(mock.call_count, len(data))

    @patch('src.cli.inputs.record_mp4_task')
    def test_record_videos_with_empty_data(self, mock):
        data = pd.DataFrame()
        version = 1.0
        output_dir = '/empty/path'

        inputs.record_videos(data, version, output_dir)

        self.assertEqual(mock.call_count, 0)

    def test_record_videos_with_invalid_output_dir(self):
        data = pd.DataFrame({"column1": [1, 2, 3], "column2": ['a', 'b', 'c']})
        version = 1.0
        output_dir = '/invalid/path'

        with self.assertRaises(FileNotFoundError):
            os.chdir(output_dir)
            inputs.record_videos(data, version, output_dir)

    @patch('builtins.input', return_value='yes')
    @patch('pandas.read_csv')
    def test_get_comments_default(self, mock_read_csv, mock_input):
        mock_read_csv.return_value = pd.DataFrame({"A": [1, 2, 3, 4]}, columns=["A"])
        result = inputs.get_comments()

        if isinstance(result, tuple):  # check if result is a tuple
            result = result[0]  # unpack DataFrame from tuple

        # Verify correct function calls were made
        mock_input.assert_called_once_with('Use default comment? (yes/no): ')
        mock_read_csv.assert_called_once_with('samples/comments.csv')

        # Verify the results
        pd.testing.assert_frame_equal(result, pd.DataFrame({"A": [1, 2, 3, 4]}, columns=["A"]))

    @patch('builtins.input', return_value='no')
    @patch('src.cli.inputs.fetch_comments')
    def test_get_comments_non_default(self, mock_fetch_comments, mock_input):
        mock_fetch_comments.return_value = pd.DataFrame({"B": [5, 6, 7, 8]}, columns=["B"])
        result = inputs.get_comments()

        if isinstance(result, tuple):  # check if result is a tuple
            result = result[0]  # unpack DataFrame from tuple

        # Verify correct function calls were made
        mock_input.assert_called_once_with('Use default comment? (yes/no): ')
        mock_fetch_comments.assert_called_once()

        # Verify the results
        pd.testing.assert_frame_equal(result, pd.DataFrame({"B": [5, 6, 7, 8]}, columns=["B"]))

    @patch('builtins.input', return_value='no')
    @patch('src.cli.inputs.fetch_comments', return_value=None)
    def test_get_comments_none(self, mock_fetch_comments, mock_input):
        result = inputs.get_comments()

        if isinstance(result, tuple):  # check if result is a tuple
            result = result[0]  # unpack DataFrame from tuple

        # Verify correct function calls were made
        mock_input.assert_called_once_with('Use default comment? (yes/no): ')
        mock_fetch_comments.assert_called_once()

        # Verify results
        self.assertIsNone(result)

    @patch('builtins.input', return_value='gtts')
    def test_get_tts_library_gtts(self, input_mocked):
        self.assertEqual(inputs.get_tts_library(), 'gtts')

    @patch('builtins.input', return_value='tts')
    def test_get_tts_library_tts(self, input_mocked):
        self.assertEqual(inputs.get_tts_library(), 'tts')

    @patch('builtins.input', side_effect=['invalid', 'gtts'])
    def test_get_tts_library_invalid_then_gtts(self, input_mocked):
        self.assertEqual(inputs.get_tts_library(), 'gtts')

    @patch('src.cli.inputs.select_version')
    def test_get_version_none(self, mock_select_version):
        # Setup
        mock_select_version.return_value = None

        # Exercise
        result = inputs.get_version()

        # Verify
        self.assertIsNone(result)
        mock_select_version.assert_called_once_with('src/html/templates')

    @patch('src.cli.inputs.select_version')
    def test_get_version_not_none(self, mock_select_version):
        # Setup
        expected_return_value = '2.0'
        mock_select_version.return_value = expected_return_value

        # Exercise
        result = inputs.get_version()

        # Verify
        self.assertEqual(result, expected_return_value)
        mock_select_version.assert_called_once_with('src/html/templates')

    def test_create_output_directory_returns_string(self):
        result = inputs.create_output_directory()
        self.assertIsInstance(result, str)

    def test_create_output_directory_creates_directory(self):
        result = inputs.create_output_directory()
        self.assertTrue(os.path.isdir(result))

    def test_create_output_directory_has_correct_prefix(self):
        result = inputs.create_output_directory()
        self.assertTrue(result.startswith(self.default_output_directory))

    def test_create_output_directory_has_correct_timestamp_format(self):
        result = inputs.create_output_directory()
        timestamp_str = result.replace(self.default_output_directory, "")
        time.strptime(timestamp_str, '%Y%m%d-%H%M%S')


if __name__ == '__main__':
    unittest.main()
