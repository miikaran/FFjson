<div align="center">
    <img src="https://github.com/user-attachments/assets/0b66068d-cd62-426c-b144-b72847cf30c4" width="100">
    <h1>JSON -> FFmpeg -> Video<h1/>
</div>
        
## Overview
This is a small proof-of-concept ***(in-progress)*** Python library designed to abstract video processing using FFmpeg with JSON mappings. Inspired by the **JSON2Video** API, this project allows for automated video creation by defining video parameters in JSON.

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
          "pixelFormat": "yuv420p",
          "codec": "h264",
          "bitRate": "2M",
          "startTime": 5,
          "duration": 10,
          "filters": {
            "scale": "1280:720",
            "fps": 30
          }
        },
        {
          "id": "clip2",
          "type": "audio",
          "file": "input2.mp3",
          "format": "mp3",
          "codec": "aac",
          "sampleRate": 44100,
          "channels": 2,
          "startTime": 2,
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
            "borderWidth": 2,
            "borderColor": "black",
            "shadowColor": "gray",
            "shadowX": 2,
            "shadowY": 2
          },
          "duration": 5
        },
        {
            "id": "clip4",
            "type": "video",
            "file": "video1.mp4",
            "start_time": 0,
            "duration": 10,
            "filters": {
                "scale": "1920x1080"
            }
        },
        {
        "id": "clip5",
        "type": "video",
        "file": "video2.mp4",
        "start_time": 0,
        "duration": 10,
        "filters": {
            "scale": "640x360",
            "overlay": "W-w-10:H-h-10"
        }
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
```
Output
```sh
ffmpeg

# Inputs
-i input1.mp4 -f mp4 -r 30 -pix_fmt yuv420p -c h264 -b:v 2M -t 10 -ss 5 \
-i video1.mp4 -t 10 \
-i video2.mp4 -t 10 \
-i input2.mp3 -f mp3 -c aac -ar 44100 -ac 2 -t 12 -ss 2 \
-i color=c=black:s=640x720:d=10 -t 5 \

# Filters
[-1:v]scale=1280:720:fps=30[0:v] \
[0:v]scale=1920x1080[1:v] \
[1:v]scale=640x360:overlay=W-w-10:H-h-10[2:v] \
[2:a]volume=0.8:aresample=44100[3:a] \
[3:v]drawtext=text=Hello, World!:fontsize=24:fontcolor=white:borderw=2:bordercolor=black:shadowcolor=gray:shadowx=2:shadowy=2[4:v] \

# Output
-map 0:video -map 1:video -map 2:video -map 3:audio -map 4:text -c:v libx264 -c:a aac final_output.mp4
```


