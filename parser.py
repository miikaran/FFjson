from typing import List, Dict

class ClipsParser:
    def __init__(self, source: List[Dict]):
        self.source = source
        self.clips_by_type = {"video": [], "audio": [], "text": []}
        self.parse_clips()

    def parse_clips(self):
        for clip in self.source:
            clip_type = clip.get("type")
            if clip_type in self.clips_by_type:
                self.clips_by_type[clip_type].append(clip)

    def get_all_clips(self) -> List[Dict]:
        return sum(self.clips_by_type.values(), [])
