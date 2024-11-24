import json

class ClipDataParser:

    def __init__(self, source):
        self.source = source
        self.clip_types = ["video", "audio", "text"]
        self.videos = []
        self.audios = []
        self.texts = []
        self.parse_clips(self.source)
    
    def parse_clips(self, clips):
        for clip in clips:
            clip_type = clip.get("type", None)
            if clip_type and clip_type in self.clip_types:
                if clip_type == "video":
                    self.videos.append(clip)
                elif clip_type == "audio":
                    self.audios.append(clip)
                elif clip_type == "text":
                    self.texts.append(clip)
    
    def get_all_clips(self):
        return self.videos + self.audios + self.texts


class ClipParser:
  
    def __init__(self, id, clip_type, filters):
        self.id = id
        self.type = clip_type
        self.filters = filters


class InputParser(ClipParser):
 
    def __init__(self, id, type, file=None, duration=None, format=None, filters=[]):
        super().__init__(id, type, filters)
        if type == "text":
            file = "color=c=black:s=640x720:d=10"
        self.file = file
        self.format = format
        self.duration = duration
        self.input_mappings = {
            "file": "-i",
            "format": "-f",
            "duration": "-t",
            "startTime": "-ss",
            "endTime": "-t"
        }
        self.input_parts = []
        if self.type in ("video", "audio", "text"):
            self.build_input()

    def build_input(self):
        for field, value in self.__dict__.items():
            ffmpeg_label = self.input_mappings.get(field)
            if ffmpeg_label and value:
                self.input_parts.append(f"{ffmpeg_label} {value}")
    
    def get_input(self):
        return " ".join(self.input_parts) if self.input_parts else None


class TrackParser(ClipParser):
    def __init__(self, id, clip_type, clip, clip_index, filters=[]):
        super().__init__(id, clip_type, filters)
        self.clip = clip
        self.clip_index = clip_index
        self.filters = self.clip.get("filters", [])
        self.filter_mappings = {
            "text": "drawtext=text",
            "fontSize": "fontsize",
            "fontColor": "fontcolor",
            "scale": "scale"
        }
        self.type_to_label_mapping = {
            "video": "v",
            "audio": "a",
            "text": "v"
        }
        self.track_parts = []
        self.build_tracks()

    def build_tracks(self):
        clip_type = self.clip.get("type")
        filters = self.clip.get("filters", {})
        if not (clip_type and filters):
            return
        type_label = self.type_to_label_mapping.get(clip_type)
        if not type_label:
            raise ValueError(f"Invalid type label for clip type: {clip_type}")    
        source_stream_specifier = f"[{self.clip_index-1}:{type_label}]"
        reference_stream_specifier = f"[{self.clip_index}:{type_label}];"
        filter_parts = [source_stream_specifier]
        for i, (filter_name, value) in enumerate(filters.items()):
            filter_part = self._process_filter(i, len(filters), filter_name, value)
            if filter_part:
                filter_parts.append(filter_part)
        filter_parts.append(reference_stream_specifier)
        self.track_parts.append("".join(filter_parts))

    def _process_filter(self, clip_index, filters_len, filter_name, value):
        filter_parts = ""
        if filter_name in self.filter_mappings:
            mapped_filter = self.filter_mappings[filter_name]
            filter_parts += f"{mapped_filter}={value}"
            if clip_index < filters_len - 1:
                filter_parts += ":"
        return filter_parts
    
    def get_tracks(self):
        return " \\".join(self.track_parts)


class JsonToFFmpeg:
    def __init__(self, json_file):
        self.json_data = self._read_json_from_file(json_file)
        clips = self._get_clips()
        self.clip_parser = ClipDataParser(clips)
        self.inputs = []
        self.tracks = []
        self.outputs = []

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
            input_parser = InputParser(**clip)
            input_part = input_parser.get_input()
            if input_part:
                self.inputs.append(input_part)
            track_parser = TrackParser(clip["id"], clip["type"], clip, i+1)
            track_part = track_parser.get_tracks()
            if track_part:
                self.tracks.append(track_part)

    def build_ffmpeg_from_parts(self):
        return " ".join(self.inputs + self.tracks + self.outputs)


if __name__ == "__main__":
    video = JsonToFFmpeg("video.json")
    video._generate_ffmpeg_parts()
    print(video.build_ffmpeg_from_parts())
