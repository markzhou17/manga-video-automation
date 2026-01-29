import os
import subprocess
from pathlib import Path
from pydub import AudioSegment

# 校验配置（与generate_video.py保持一致）
TARGET_RESOLUTION = (1080, 1920)  # 宽×高
MIN_VIDEO_DURATION = 5  # 最小视频时长（秒）
MAX_AUDIO_VOLUME = -10  # 最小音频音量（dB，避免无声，-20~0为正常）
FINAL_VIDEO = Path("output/final_video.mp4")

def get_video_info():
    """用ffprobe获取视频分辨率和时长"""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration",
        "-of", "csv=p=0",
        str(FINAL_VIDEO)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = result.stdout.strip().split(",")
    return int(info[0]), int(info[1]), float(info[2])

def get_audio_volume():
    """获取音频平均音量（dB）"""
    audio = AudioSegment.from_file(FINAL_VIDEO, format="mp4")
    return audio.dBFS

def validate_video():
    # 1. 检查最终视频是否存在
    if not FINAL_VIDEO.exists():
        raise Exception(f"未找到生成的最终视频：{FINAL_VIDEO}，视频生成失败！")
    
    # 2. 校验分辨率
    w, h, duration = get_video_info()
    if (w, h) != TARGET_RESOLUTION:
        raise Exception(f"视频分辨率不符合要求！预期：{TARGET_RESOLUTION}，实际：{w}×{h}")
    
    # 3. 校验视频时长
    if duration < MIN_VIDEO_DURATION:
        raise Exception(f"视频时长过短！预期≥{MIN_VIDEO_DURATION}秒，实际：{duration:.1f}秒")
    
    # 4. 校验音频音量
    audio_volume = get_audio_volume()
    if audio_volume < MAX_AUDIO_VOLUME:
        raise Exception(f"音频音量过低！预期≥{MAX_AUDIO_VOLUME}dB，实际：{audio_volume:.1f}dB")
    
    # 所有校验通过
    print("="*50)
    print(f"视频质量校验通过！")
    print(f"分辨率：{w}×{h}")
    print(f"时长：{duration:.1f}秒")
    print(f"音频平均音量：{audio_volume:.1f}dB")
    print("="*50)

if __name__ == "__main__":
    validate_video()
