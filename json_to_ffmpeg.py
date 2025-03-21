from parser import ClipsParser
from utils import Output
from clips import Input, Track
import json

class JsonToFFmpeg:
    def __init__(self, json_file, config_file, output_file="output.mp4"):
        self.json_data = self._read_json_from_file(json_file)
        self.config_data = self._read_json_from_file(config_file)
        self.output_file = output_file
        clips = self._get_clips()
        self.clip_parser = ClipsParser(clips)
        self.inputs = []
        self.tracks = []
        self.maps = []
        self.output_options = Output(output_file=self.output_file)

    def _read_json_from_file(self, json_file):
        try:
            with open(json_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid or missing JSON file: {e}")

    def _get_clips(self):
        return self.json_data.get("clips", [])

    def _generate_ffmpeg_parts(self):
        all_clips = self.clip_parser.get_all_clips()
        for i, clip in enumerate(all_clips):
            input_parser = Input(clip, self.config_data)
            input_part = input_parser.get_input()
            if input_part:
                self.inputs.append(input_part)
            track_parser = Track(clip, i, self.config_data)
            track_part = track_parser.get_tracks()
            if track_part:
                self.tracks.append(track_part)

            self.maps.append(f"-map {i}:{clip.get('type', 'v')}")
        
        self.output_options = self.output_options.build_output()

    def build_ffmpeg_from_parts(self):
        self._generate_ffmpeg_parts()
        return "ffmpeg " + " ".join(self.inputs + self.tracks + self.maps + [self.output_options])