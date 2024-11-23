import json

CATEGORY_TO_OPTION_MAPPING = {
    "input": {
        "duration": "-t",
        "format": "-f",
        "startTime": "-ss",
        "endTime": "-t",
        "src": "-i",
    },
    "output": {
        "video": {
            "format": "-f",
            "codec": "-c:v",
            "bitrate": "-b:v",
        },
        "audio": {
            "format": "-f",
            "codec": "-c:a",
            "bitrate": "-b:a",
        },
    },
    "filter": {
        "fontSize": "fontsize",
        "fontColor": "fontcolor",
        "width": "width",
        "height": "height",
    },
}


class JsonToFFmpeg:
  
    IGNORED_OPTIONS = {"id", "type", "text"}
    SOURCE_TYPES = {"video", "audio"}

    def __init__(self, json_file) -> None:
        self.json_data = self._read_json_from_file(json_file)
        self.elements = self._get_all_elements()

    @staticmethod
    def _read_json_from_file(json_file):
        try:
            with open(json_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid or missing JSON file: {e}")

    def _get_all_elements(self):
        elements = self.json_data.get("elements", [])
        for scene in self.json_data.get("scenes", []):
            elements.extend(scene.get("elements", []))
        return elements

    def _process_filter_settings(self, settings, options, element_index, element_type):
        type_label = element_type[0]
        filter_parts = [f"[{element_index}:{type_label}]"]
        for idx, (filter_key, filter_value) in enumerate(settings.items()):
            if filter_key in options:
                filter_parts.append(f"{options[filter_key]}={filter_value}")
                if idx < len(settings) - 1:
                    filter_parts.append(":")
        filter_parts.append(f"[{element_index + 1}:{type_label}];")
        return "".join(filter_parts)

    def _generate_part(self, category):
        if category not in CATEGORY_TO_OPTION_MAPPING:
            return "" 
        options = CATEGORY_TO_OPTION_MAPPING[category]
        command_parts = []
        for i, element in enumerate(self.elements):
            element_type = element.get("type")
            if (category in ["input", "output"]) and element_type not in self.SOURCE_TYPES:
                continue
            for key, value in element.items():
                if key in self.IGNORED_OPTIONS:
                    continue
                if key == "settings" and category == "filter":
                    filter = self._process_filter_settings(value, options, i, element_type)
                    command_parts.append(filter)
                elif key in options:
                    command_parts.append(f"{options[key]} {value}")
        return " ".join(command_parts)

    def json_to_ffmpeg(self) -> str:
        command_parts = ["ffmpeg"]
        for category in CATEGORY_TO_OPTION_MAPPING:
            part = self._generate_part(category)
            if part: command_parts.append(part)
        return " ".join(command_parts)


if __name__ == "__main__":
    video = JsonToFFmpeg("video.json")
    print(video.json_to_ffmpeg())
