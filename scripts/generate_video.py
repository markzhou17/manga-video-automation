import os
import subprocess
from pathlib import Path

# 配置参数（按需修改，新手建议保持默认）
IMAGE_DISPLAY_TIME = 3  # 每张图片显示秒数
FADE_TIME = 1  # 淡入淡出转场秒数
VIDEO_RESOLUTION = "1080x1920"  # 9:16竖屏，横屏改为1920x1080
AUDIO_VOLUME = "1.0"  # 音频音量（0.5=50%，2.0=200%）
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# 目录定义
PROCESS_IMG_DIR = Path("source/manga/processed")
SCRIPT_FILE = Path("source/scripts/script.txt")

def generate_video():
    # 1. 检查预处理后的图片和解说文案是否存在
    img_files = sorted(PROCESS_IMG_DIR.glob("*.png"))
    if not img_files:
        raise Exception(f"在{PROCESS_IMG_DIR}中未找到预处理后的图片，请先执行preprocess.py！")
    if not SCRIPT_FILE.exists():
        raise Exception(f"未找到解说文案：{SCRIPT_FILE}，请在source/scripts/下创建script.txt！")
    print(f"开始生成视频，共{len(img_files)}张图片，解说文案：{SCRIPT_FILE}")

    # 2. 生成FFmpeg图片列表文件（解决图片序号问题）
    img_list_file = Path("image_list.txt")
    with open(img_list_file, "w", encoding="utf-8") as f:
        for img in img_files:
            f.write(f"file '{img.absolute()}'\n")
            f.write(f"duration {IMAGE_DISPLAY_TIME}\n")
    # 最后一张图片需要额外加一行（FFmpeg concat格式要求）
    with open(img_list_file, "a", encoding="utf-8") as f:
        f.write(f"file '{img_files[-1].absolute()}'\n")

    # 3. 用FFmpeg拼接图片生成无音频视频（带淡入淡出转场）
    temp_video = Path("temp_video.mp4")
    ffmpeg_video_cmd = [
        "ffmpeg", "-y",  # -y 覆盖已有文件
        "-f", "concat", "-safe", "0", "-i", str(img_list_file),
        "-vf", f"fade=t=in:st=0:d={FADE_TIME},fade=t=out:st={len(img_files)*IMAGE_DISPLAY_TIME-FADE_TIME}:d={FADE_TIME},scale={VIDEO_RESOLUTION}:force_original_aspect_ratio=1",
        "-r", "30",  # 视频帧率
        "-c:v", "libx264",  # 视频编码器
        "-pix_fmt", "yuv420p",  # 色彩格式（适配所有播放器）
        "-crf", "23",  # 视频质量（0-51，23为默认，越小质量越高）
        str(temp_video)
    ]
    subprocess.run(ffmpeg_video_cmd, check=True, capture_output=True, text=True)
    print(f"无音频视频生成完成：{temp_video}")

    # 4. Edge TTS生成解说音频（免费，多语言支持，默认中文）
    audio_file = Path("audio.mp3")
    tts_cmd = [
        "edge-tts",
        "--voice", "zh-CN-XiaoxiaoNeural",  # 中文女声（可替换为zh-CN-YunxiNeural男声）
        "--text", open(SCRIPT_FILE, "r", encoding="utf-8").read(),
        "--write-media", str(audio_file),
        "--write-subtitles", "sub.srt"  # 可选：生成字幕文件
    ]
    subprocess.run(tts_cmd, check=True, capture_output=True, text=True)
    print(f"解说音频生成完成：{audio_file}")

    # 5. 音视频融合（调整音频音量，保证视频和音频时长匹配）
    final_video = OUTPUT_DIR / "final_video.mp4"
    ffmpeg_merge_cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(audio_file),
        "-filter:a", f"volume={AUDIO_VOLUME}",  # 调整音频音量
        "-c:v", "copy",  # 视频流直接复制，不重新编码（提速）
        "-c:a", "aac",  # 音频编码器（适配短视频平台）
        "-b:a", "192k",  # 音频码率
        "-shortest",  # 取视频和音频中较短的时长（避免黑屏/无声）
        str(final_video)
    ]
    subprocess.run(ffmpeg_merge_cmd, check=True, capture_output=True, text=True)
    print(f"音视频融合完成，最终视频：{final_video}")

    # 6. 清理临时文件
    for f in [img_list_file, temp_video, audio_file, Path("sub.srt")]:
        if f.exists():
            f.unlink()
    print("临时文件清理完成，视频生成流程结束！")

if __name__ == "__main__":
    generate_video()
