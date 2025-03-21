
class Clip:
    def __init__(self, id, clip_type, filters):
        self.id = id
        self.type = clip_type
        self.filters = filters

class Input(Clip):
    def __init__(self, clip, config):
        super().__init__(clip["id"], clip["type"], clip.get("filters", []))
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
        super().__init__(clip["id"], clip["type"], clip.get("filters", []))
        self.clip = clip
        self.clip_index = clip_index
        self.config = config
        self.filters = self.clip.get("filters", {})
        self.additional_options = clip.get("additionalOptions", [])

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
