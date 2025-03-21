from json_to_ffmpeg import JsonToFFmpeg
import logging

if __name__ == "__main__":
    video_json_file = "data/video.json" 
    config_json_file = "data/ffmpeg.json" 
    output_file = "final_output.mp4"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        ffmpeg_generator = JsonToFFmpeg(video_json_file, config_json_file, output_file)
        ffmpeg_command = ffmpeg_generator.build_ffmpeg_from_parts()
        print("Generated FFmpeg Command:")
        print(ffmpeg_command)
    except Exception as e:
        logging.error(f"Error generating FFmpeg command: {e}")