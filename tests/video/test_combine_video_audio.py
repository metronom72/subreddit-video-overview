import os
import unittest
from unittest import mock
from unittest.mock import MagicMock
from src.video.combine_video_audio import combine_video_audio


class TestCombineVideoAudio(unittest.TestCase):

    @mock.patch('os.path.isfile')
    @mock.patch('src.video.combine_video_audio.VideoFileClip')
    @mock.patch('src.video.combine_video_audio.AudioFileClip')
    def test_combine_video_audio_valid(self, mock_audio_clip, mock_video_clip, mock_isfile):
        # Mock functions
        mock_isfile.return_value = True
        mock_audio_clip_instance = MagicMock()
        mock_audio_clip_instance.set_start.return_value = mock_audio_clip_instance
        mock_audio_clip.return_value = mock_audio_clip_instance
        mock_video_clip_instance = MagicMock()
        mock_video_clip_instance.set_audio.return_value = mock_video_clip_instance
        mock_video_clip.return_value = mock_video_clip_instance

        # Call Function
        combine_video_audio("valid_video.mp4", "valid_audio.mp3", "output_video.mp4")

        # Asserts
        mock_isfile.assert_any_call("valid_video.mp4")
        mock_isfile.assert_any_call("valid_audio.mp3")
        mock_video_clip.assert_called_once_with("valid_video.mp4")
        mock_audio_clip.assert_called_once_with("valid_audio.mp3")
        mock_audio_clip_instance.set_start.assert_called_once_with(2)
        mock_video_clip_instance.set_audio.assert_called_once_with(mock_audio_clip_instance)
        mock_video_clip_instance.write_videofile.assert_called_once_with("output_video.mp4", codec="libx264", audio_codec="aac")

    @mock.patch('os.path.isfile')
    def test_combine_video_audio_invalid_video(self, mock_isfile):
        # Mock functions
        mock_isfile.side_effect = [False, True]

        # Asserts
        with self.assertRaises(ValueError) as cm:
            combine_video_audio("invalid_video.mp4", "valid_audio.mp3", "output_video.mp4")
        self.assertEqual(str(cm.exception), "Invalid video file path: invalid_video.mp4")

    @mock.patch('os.path.isfile')
    def test_combine_video_audio_invalid_audio(self, mock_isfile):
        # Mock functions
        mock_isfile.side_effect = [True, False]

        # Asserts
        with self.assertRaises(ValueError) as cm:
            combine_video_audio("valid_video.mp4", "invalid_audio.mp3", "output_video.mp4")
        self.assertEqual(str(cm.exception), "Invalid audio file path: invalid_audio.mp3")


if __name__ == '__main__':
    unittest.main()