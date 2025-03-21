from typing import Dict

class Subtitle:
    def __init__(self, subtitle_data: Dict):
        self.text = subtitle_data.get("text", "")
        self.start_time = subtitle_data.get("start_time", 0)
        self.end_time = subtitle_data.get("end_time", 5)
        self.position = subtitle_data.get("position", "bottom")
        self.color = subtitle_data.get("color", "white")
        self.font = subtitle_data.get("font", "Arial")

    def generate_subtitle_command(self) -> str:
        position_map = {"bottom": "10:10", "top": "10:main_h-10", "center": "main_w/2:main_h/2"}
        position = position_map.get(self.position, "10:10")
        return f"drawtext=text='{self.text}':x={position}:fontcolor={self.color}:fontsize=24:fontfile='{self.font}'"
    
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
    
class Scene:
    def __init__(self, scene_data: Dict, config: Dict):
        self.id = scene_data.get("id")
        self.clips = scene_data.get("clips", [])
        self.nested_scenes = scene_data.get("nestedScenes", [])
        self.transitions = scene_data.get("transitions", [])
        self.effects = scene_data.get("effects", [])
        self.timeline = scene_data.get("timeline", [])
        self.config = config
        self.scene_parts = []

    def build_scene(self):
        for nested_scene in self.nested_scenes:
            nested_scene_obj = Scene(nested_scene, self.config)
            nested_scene_obj.build_scene()
            self.scene_parts.append(nested_scene_obj.get_scene())

        for clip_index, clip in enumerate(self.clips):
            source_specifier = f"[{clip_index}:v]"
            transition_filter = self._apply_transitions(clip_index)
            effect_filter = self._apply_effects(clip_index)
            if transition_filter:
                self.scene_parts.append(f"{source_specifier}{transition_filter}")
            if effect_filter:
                self.scene_parts.append(f"{source_specifier}{effect_filter}")

    def _apply_transitions(self, clip_index):
        if clip_index < len(self.transitions):
            transition = self.transitions[clip_index]
            if transition == "wipe":
                return "wipe=duration=1:angle=90"
            elif transition == "zoom":
                return "zoompan=z='zoom+0.1':d=25"
            elif transition == "slide":
                return "slide=duration=1:direction=left"
        return ""

    def _apply_effects(self, clip_index):
        if clip_index < len(self.effects):
            effect = self.effects[clip_index]
            if effect == "blur":
                return "boxblur=luma_radius=2:luma_power=1"
            elif effect == "keying":
                return "colorkey=color=green:similarity=0.1"
        return ""

    def get_scene(self) -> str:
        return " \\".join(self.scene_parts)
