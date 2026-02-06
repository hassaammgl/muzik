from src.tools.file_managers import FileManager
from pathlib import Path
import ffmpeg
from src.tools.prompter import Prompter

manager = FileManager()
prompter = Prompter()


class AudioConverter:
    def __init__(self):
        self.init()

    def init(self):
        prompts = [
            {"prompt": "", "value": "player"},
            {"prompt": "Converter", "value": "converter"},
            {"prompt": "Downloader", "value": "downloader"},
            {"prompt": "Settings", "value": "settings"},
        ]

        prompter.prompt(
            heading="Select one option from them",
            options=prompts,
            instructions="Select one option please",
            user_choice=prompts[0]["value"],
        )

    def convert_audio(self, input_file: str, output_file: str):
        """
        convert audio file to another format
        Example: mp3 -> wav
        """
        input_file = str(Path(input_file).resolve())
        output_file = str(Path(output_file).resolve())

        ffmpeg.input(input_file).output(output_file, acodec="acc").run(
            overwrite_output=True
        )
        print(f"Audio converted: {output_file}")

    def extract_audio_from_video(self, video_file: str, output_file: str):
        """
        Extract Audio from Video file.
        """
        video_file = str(Path(video_file).resolve())
        output_file = str(Path(output_file).resolve())

        ffmpeg.input(video_file).output(output_file, vn=True, acodec="aac").run(
            overwrite_output=True
        )
        print(f"Audio Extracted: {output_file}")

    def convert_video(self, input_file: str, output_file: str):
        """
        Convert video to another format.
        """

        input_file = str(Path(input_file).resolve())
        output_file = str(Path(output_file).resolve())

        ffmpeg.input(input_file).output(
            output_file, vcodec="libx264", acodec="aac"
        ).run(overwrite_output=True)
        print(f"Video converted: {output_file}")
