import unittest
from moviepy.editor import VideoFileClip, ColorClip
import os
from src.video.adjust_video_length import adjust_video_length


class TestAdjustVideoLength(unittest.TestCase):
    def setUp(self):
        # Define input video, output video locations and target length for testing
        self.input_video = './input.mp4'
        self.output_video = './output.mp4'
        self.target_length = 10

        # Create a mock input video file with fps specified
        clip = ColorClip(size=(640, 480), color=(255, 0, 0), duration=5)  # 5-second red video
        clip = clip.set_fps(24)
        clip.write_videofile(self.input_video, codec='libx264')

    def test_adjust_video_length(self):
        # Adjust the video length
        adjust_video_length(self.input_video, self.output_video, self.target_length)
        self.assertTrue(os.path.exists(self.output_video),
                        'An output video file should have been created but was not found.')

        # Load the output video file and check its duration
        video_clip = VideoFileClip(self.output_video)
        # Add 3 to target length as it's added in adjust_video_length function
        expected_duration = self.target_length + 3
        self.assertEqual(video_clip.duration, expected_duration,
                         f'Expected video length to be {expected_duration}, but got {video_clip.duration}')

    def tearDown(self):
        # Clean up created files
        if os.path.exists(self.input_video):
            os.remove(self.input_video)
        if os.path.exists(self.output_video):
            os.remove(self.output_video)


if __name__ == "__main__":
    unittest.main()
