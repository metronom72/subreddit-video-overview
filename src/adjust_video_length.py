from moviepy.editor import VideoFileClip, vfx


def adjust_video_length(input_video, output_video, target_length):
    """
    Adjusts the length of a video by changing the playback speed.

    :param input_video: Path of the input video file.
    :type input_video: str
    :param output_video: Path of the output video file.
    :type output_video: str
    :param target_length: Target length of the output video in seconds.
    :type target_length: int
    :return: None
    """

    # Load the video clip
    video_clip = VideoFileClip(input_video)

    # Original and desired duration
    original_duration = video_clip.duration  # seconds
    desired_duration = target_length + 3  # seconds

    # Calculate the speed factor
    speed_factor = original_duration / desired_duration

    # Change playback speed
    modified_clip = video_clip.fx(vfx.speedx, factor=speed_factor)

    # Write the result to a file
    modified_clip.write_videofile(output_video, codec="libx264")
