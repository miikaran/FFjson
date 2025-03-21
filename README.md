# JSON -> FFmpeg -> Video

## Overview
This is a proof-of-concept (in-progress) Python library designed to abstract video processing using FFmpeg with JSON mappings. Inspired by the **JSON2Video** API, this project allows for automated video creation by defining video parameters in JSON.

## Features
- Convert JSON into FFmpeg command-line arguments.
- Automate video processing with structured data.
- Easily configurable and extensible for different video processing needs.

## Installation
To use this library, ensure you have FFmpeg installed on your system. You can install it via:

```sh
# On macOS using Homebrew
brew install ffmpeg

# On Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# On Windows (via Chocolatey)
choco install ffmpeg
```

```sh
# Clone the repository
git clone https://github.com/your-username/json-ffmpeg-video.git

# Navigate to the project folder
cd json-ffmpeg-video
```

## Usage
Example JSON Input, found in -> ***data/video.json***
```json
{
    "id": "12345",
    "comment": "Test video",
    "resolution": [1920, 1080],
    "fps": 30,
    "clips": [
        {
          "id": "clip1",
          "type": "video",
          "file": "input1.mp4",
          "format": "mp4",
          "frameRate": 30,
          "startTime": 1,
          "duration": 10,
        },
        {
          "id": "clip2",
          "type": "audio",
          "file": "input2.mp3",
          "format": "mp3",
          "codec": "aac",
          "startTime": 0,
          "duration": 12,
          "filters": {
            "volume": "0.8",
            "aresample": 44100
          }
        },
        {
          "id": "clip3",
          "type": "text",
          "filters": {
            "text": "Hello, World!",
            "fontSize": 24,
            "fontColor": "white",
          },
          "duration": 5
        }
      ],
      "scenes": [
        {
          "id": "scene1",
          "clips": ["clip1", "clip2"],
          "transitions": ["wipe", "fade"],
          "effects": ["blur", "keying"]
        }
      ],
      "subtitles": [
        {
          "text": "This is a subtitle!",
          "start_time": 0,
          "end_time": 5,
          "position": "bottom",
          "color": "yellow",
          "font": "Arial.ttf"
        }
      ]
  }

