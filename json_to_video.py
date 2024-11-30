import json


class ClipsParser:
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


class Clip:
    def __init__(self, id, clip_type, filters):
        self.id = id
        self.type = clip_type
        self.filters = filters


class Input(Clip):
    def __init__(self, clip, config):
        super().__init__(
            clip["id"], 
            clip["type"], 
            clip.get("filters", [])
        )
        self.clip = clip
        self.config = config
        self.file = "color=c=black:s=640x720:d=10" if clip["type"] == "text" else clip.get("file")
        self.format = clip.get("format")
        self.frame_rate = clip.get("frameRate")
        self.pixel_format = clip.get("pixelFormat")
        self.codec = clip.get("codec")
        self.bit_rate = clip.get("bitRate")
        self.sample_rate = clip.get("sampleRate")
        self.channels = clip.get("channels")
        self.duration = clip.get("duration")
        self.start_time = clip.get("startTime")
        self.end_time = clip.get("endTime")
        self.additional_options = clip.get("additionalOptions", [])

        # Use mappings from config
        self.input_mappings = self.config["input_mappings"]
        self.input_parts = []
        if self.type in ("video", "audio", "text"):
            self.build_input()

    def build_input(self):
        for field, value in self.__dict__.items():
            ffmpeg_label = self.input_mappings.get(field)
            if ffmpeg_label and value:
                self.input_parts.append(f"{ffmpeg_label} {value}")
        if self.additional_options:
            self.input_parts.extend(self.additional_options)
    
    def get_input(self):
        return " ".join(self.input_parts) if self.input_parts else None


class Track(Clip):
    def __init__(self, clip, clip_index, config):
        super().__init__(
            clip["id"], 
            clip["type"], 
            clip.get("filters", [])
        )
        self.clip = clip
        self.clip_index = clip_index
        self.config = config
        self.filters = self.clip.get("filters", {})
        self.additional_options = clip.get("additionalOptions", [])
        
        # Use mappings from config
        self.filter_mappings = self.config["filter_mappings"]
        self.type_to_label_mapping = self.config["type_to_label_mapping"]
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
        reference_stream_specifier = f"[{self.clip_index}:{type_label}]"
        filter_parts = [source_stream_specifier]
        for i, (filter_name, value) in enumerate(filters.items()):
            filter_part = self._process_filter(i, len(filters), filter_name, value)
            if filter_part:
                filter_parts.append(filter_part)
        filter_parts.append(reference_stream_specifier)
        self.track_parts.append("".join(filter_parts))
        if self.additional_options:
            self.track_parts.extend(self.additional_options)

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


class Output:
    def __init__(self, output_file="output.mp4", codec="libx264", audio_codec="aac", resolution=None, additional_options=None):
        self.output_file = output_file
        self.codec = codec
        self.audio_codec = audio_codec
        self.resolution = resolution
        self.additional_options = additional_options or []

    def build_output(self):
        output_parts = [f"-c:v {self.codec}", f"-c:a {self.audio_codec}"]
        if self.resolution:
            output_parts.append(f"-s {self.resolution}")
        output_parts.extend(self.additional_options)
        output_parts.append(self.output_file)
        return " ".join(output_parts)


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
            track_parser = Track(clip, i+1, self.config_data)
            track_part = track_parser.get_tracks()
            if track_part:
                self.tracks.append(track_part)
            self.maps.append(f"-map {i}:{clip.get('type', 'v')}")
        
        self.output_options = self.output_options.build_output()

    def build_ffmpeg_from_parts(self):
        self._generate_ffmpeg_parts()
        return "ffmpeg " + " ".join(self.inputs + self.tracks + self.maps + [self.output_options])


if __name__ == "__main__":
    video = JsonToFFmpeg("video.json", "config.json", "final_output.mp4")
    print(video.build_ffmpeg_from_parts())
