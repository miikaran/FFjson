import json
from dataclasses import dataclass, field, fields

@dataclass
class ClipParser():

    CLIP_TYPES:list = field(
        init=False, 
        default_factory=["video", "audio", "text"]
    )
    videos:list = field(init=False)
    audios:list = field(init=False)
    texts:list = field(init=False)
    source:list

    def __post_init__(self):
        self.parse_clips(self.source)
    
    def parse_clips(self, clips):
        for clip in enumerate(clips):
            type = clip.get("type", None)
            if not (type and type in self.CLIP_TYPES):
                continue
            if type == "video":
                self.videos.append(clip)
            elif type == "audio":
                self.audios.append(clip)
            elif type == "text":
                self.texts.append(clip)
    
    def get_all_clips(self):
        return [getattr(clip) for clip in fields(self)]




@dataclass
class InputParser():

    inputMappings = {
            "file": "-i",
            "format": "-f",
            "duration": "-t",
            "startTime": "-ss",
            "endTime": "-t"
        }
    type:str
    file:str
    format:str
    duration:int
    start_time:int
    end_time:int

    input_parts:list = field(init=False)

    def __post_init__(self):
        if type in ("video", "audio"):
            self.build_input()

    def build_input(self):
        for field in fields(self):
            ffmpeg_label = self.inputMappings.get(field.name, None)
            field_value = getattr(self, field)
            if not (ffmpeg_label and field_value):
                continue
            part = f"{ffmpeg_label} {field_value}"
            self.input_parts.append(part)
    
    def get_input(self):
        if not self.input_parts:
            print("No inputs found")
            return
        return " ".join(self.input_parts)
    

@dataclass
class TrackParser():

    filter_mappings = {
        "text": "drawtext=text",
        "fontSize": "fontsize",
        "fontColor": "fontcolor",
        "scale": "scale"
    }
    type_to_label_mapping = {
        "video": "v",
        "audio": "a",
    }
    clips:list
    track_parts:list = field(
        init=False, 
        default_factory=[]
        )

    def __post_init__(self):
        self.build_tracks()

    def build_tracks(self):
        for i, clip in enumerate(self.clips):
            type = clip.get("type", None)
            filters = clip.get("filters", None)
            if not (type and filters):
                continue
            for i, (filter, value) in enumerate(filters.items()):
                track_part = self._process_filter(type, i, len(filters), filter, value)
                if not track_part:
                    continue
                self.track_parts.append(track_part)

    def _process_filter(self, clip_type, clip_index, filters_len, filter, value):
        type_label = self.type_to_label_mapping.get(clip_type, None)
        if not type_label:
            print(f"Type label not found for clip type: {clip_type}")
            return
        source_stream_specifier = f"[{clip_index}:{type_label}]"
        reference_stream_specifier = f"[{clip_index}:{type_label}];"
        filter_parts = [source_stream_specifier]
        if filter in self.filter_mappings:
            mapped_filter = self.filter_mappings.get(filter, None)
            if not mapped_filter:
                return
            filter_parts.append(f"{mapped_filter}={value}")
            if clip_index < filters_len - 1:
                filter_parts.append(":")
        filter_parts.append(reference_stream_specifier)
        return " ".join(filter_parts)
    
    def get_tracks(self):
        if not self.track_parts:
            print("No tracks found")
            return
        return "\\".join(self.track_parts)
    

class JsonToFFmpeg():

    inputs:list     = []
    tracks:list     = []
    outputs:list    = []

    json_data:dict  = {}
    clip_parser     = None

    def __init__(self, json_file):
        self.json_data = self._read_json_from_file(json_file)
        clips = self._get_clips()
        self.clip_parser = ClipParser(clips)

    @staticmethod
    def _read_json_from_file(json_file):
        try:
            with open(json_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid or missing JSON file: {e}")

    def _get_clips(self):
        return self.json_data.get("clips", [])
    
    def _generate_ffmpeg_parts(self):
        all_clips = self.clip_parser.get_all_clips()
        for clip in all_clips:
            input_parser = InputParser(**clip)
            input_part = input_parser.get_input()
            if not input_part:
                continue
            self.inputs.append(input_part)
            track_parser = TrackParser(**clip)
            track_part = track_parser.get_tracks()
            if not track_part:
                continue
            self.tracks.append(track_part)
    
    def build_ffmpeg_from_parts(self):
        return " ".join([self.input, self.tracks, self.output])
        

if __name__ == "__main__":
    video = JsonToFFmpeg("video.json")
    video._generate_ffmpeg_parts()
    print(video.inputs)
