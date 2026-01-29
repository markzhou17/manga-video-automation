import os
from pathlib import Path
from PIL import Image

# 配置参数（可按需修改：横屏改为1920,1080）
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
TARGET_ASPECT = TARGET_WIDTH / TARGET_HEIGHT  # 9:16=0.5625

# 目录定义
SOURCE_DIR = Path("source/manga")
PROCESS_DIR = Path("source/manga/processed")
PROCESS_DIR.mkdir(exist_ok=True, parents=True)

def preprocess_image(img_path):
    """预处理单张图片：裁剪为目标比例，缩放到目标分辨率，补黑边"""
    with Image.open(img_path) as img:
        # 1. 转换为RGB（避免透明通道问题）
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img_w, img_h = img.size
        img_aspect = img_w / img_h

        # 2. 裁剪为目标比例（保留中心区域）
        if img_aspect > TARGET_ASPECT:
            # 原图偏宽，裁剪左右
            new_w = int(img_h * TARGET_ASPECT)
            x0 = (img_w - new_w) // 2
            img = img.crop((x0, 0, x0 + new_w, img_h))
        elif img_aspect < TARGET_ASPECT:
            # 原图偏高，裁剪上下
            new_h = int(img_w / TARGET_ASPECT)
            y0 = (img_h - new_h) // 2
            img = img.crop((0, y0, img_w, y0 + new_h))

        # 3. 缩放到目标分辨率
        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

        # 4. 保存处理后的图片（覆盖原序号，格式为PNG）
        save_name = img_path.name.split(".")[0] + ".png"
        save_path = PROCESS_DIR / save_name
        img.save(save_path, quality=95, optimize=True)
        print(f"预处理完成：{save_path}")

if __name__ == "__main__":
    # 获取所有图片文件（按序号排序）
    img_ext = (".png", ".jpg", ".jpeg", ".bmp")
    img_files = sorted([f for f in SOURCE_DIR.glob("*") if f.suffix.lower() in img_ext])
    if not img_files:
        raise Exception(f"在{SOURCE_DIR}中未找到图片文件，请检查素材！")
    
    # 批量预处理
    for f in img_files:
        preprocess_image(f)
    print(f"所有图片预处理完成，共{len(img_files)}张，保存到：{PROCESS_DIR}")
