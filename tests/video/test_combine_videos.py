import tempfile
import unittest
import os
from unittest import mock

from src.video import combine_videos
from src.video.combine_videos import create_file_list


class TestCombineVideos(unittest.TestCase):

    def setUp(self):
        self.directory = './test_directory'
        self.file_list_path = './test_file_list.txt'
        os.makedirs(self.directory, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.file_list_path):
            os.unlink(self.file_list_path)
        for file in os.listdir(self.directory):
            os.unlink(os.path.join(self.directory, file))
        os.rmdir(self.directory)

    def test_create_file_list(self):
        # Arrange
        test_filenames = ['test1_with_audio.mp4', 'test2_with_audio.mp4', 'test3.txt']
        for filename in test_filenames:
            open(os.path.join(self.directory, filename), 'a').close()

        # Act
        create_file_list(self.directory, self.file_list_path)

        # Assert
        with open(self.file_list_path, 'r') as f:
            contents = f.read()
        for filename in ['test1_with_audio.mp4', 'test2_with_audio.mp4']:
            self.assertIn(f"file '{filename}'", contents)

    def test_empty_directory(self):
        # Arrange
        # The directory is created empty in setUp

        # Act
        create_file_list(self.directory, self.file_list_path)

        # Assert
        with open(self.file_list_path, 'r') as f:
            contents = f.read()
        self.assertEqual(contents, '')

    @mock.patch('subprocess.run')
    @mock.patch('os.remove')
    @mock.patch('src.video.combine_videos.create_file_list')
    def test_concatenate_videos_success(self, mock_create_file_list, mock_os_remove, mock_subprocess_run):
        mock_subprocess_run.return_value = None
        with tempfile.TemporaryDirectory() as tmpdir:
            combine_videos.concatenate_videos(tmpdir, 'output.mp4')
            mock_create_file_list.assert_called_once_with(tmpdir, os.path.join(tmpdir, 'file_list.txt'))
            mock_subprocess_run.assert_called_once_with([
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmpdir, 'file_list.txt'),
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-c:a', 'aac',
                '-b:a', '192k', 'output.mp4'
            ], check=True)
            mock_os_remove.assert_called_once_with(os.path.join(tmpdir, 'file_list.txt'))

    @mock.patch('subprocess.run')
    @mock.patch('os.remove')
    @mock.patch('src.video.combine_videos.create_file_list')
    def test_concatenate_videos_error(self, mock_create_file_list, mock_os_remove, mock_subprocess_run):
        mock_subprocess_run.side_effect = Exception()
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(Exception):
                combine_videos.concatenate_videos(tmpdir, 'output.mp4')
            mock_create_file_list.assert_called_once_with(tmpdir, os.path.join(tmpdir, 'file_list.txt'))
            mock_subprocess_run.assert_called_once_with([
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmpdir, 'file_list.txt'),
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-c:a', 'aac',
                '-b:a', '192k', 'output.mp4'
            ], check=True)
            mock_os_remove.assert_called_once_with(os.path.join(tmpdir, 'file_list.txt'))


if __name__ == '__main__':
    unittest.main()
