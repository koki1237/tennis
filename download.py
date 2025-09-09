import os
import time
import yt_dlp
import csv

# ==== 参数 ====
SAVE_DIR = "videos"   # 保存目录
CSV_PATH = "videos.csv"    # CSV列表，格式: tournament;name;yt_id
os.makedirs(SAVE_DIR, exist_ok=True)

# ==== 工具函数 ====

def sanitize_filename(name):
    """清洗文件名，去掉非法字符"""
    return name.replace('/', '-').replace(' ', '_').replace("'", "_").replace('"', "_")

def download_video(url, save_path=".", filename=None):
    """下载单个视频"""
    if filename is None:
        output_template = os.path.join(save_path, '%(title)s.%(ext)s')
    else:
        filename = sanitize_filename(filename)
        output_template = os.path.join(save_path, filename + '.%(ext)s')

    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',  # ⭐ 合并成mp4
        'noplaylist': True,
        'quiet': False,
        'keepvideo': False,  # ⭐ 不保留中间文件（节省空间），要保留可以设True
        'concurrent_fragment_downloads': 5,  # ⭐ 多线程加速
        'postprocessors': [{
            'key': 'FFmpegMerger',
        }],
        # 'cookiefile': 'cookies.txt', # 如果需要登录，可以用cookie
    }

    try:
        start_time = time.time()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\n📥 Downloading from: {url}")
            info_dict = ydl.extract_info(url, download=True)
        end_time = time.time()

        # --- 打印视频分辨率 ---
        width = info_dict.get('width', None)
        height = info_dict.get('height', None)
        fps = info_dict.get('fps', None)
        if width and height:
            print(f"🎯 Downloaded resolution: {width}x{height} @ {fps}fps")
        else:
            print("⚠️ Warning: resolution not available.")

        print(f"✅ Download finished in {end_time - start_time:.2f} seconds\n")

    except Exception as e:
        print(f"❌ Error downloading {url}: {e}\n")

def download_all_from_csv(csv_path, save_dir):
    """根据CSV下载多个视频"""
    os.makedirs(save_dir, exist_ok=True)

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            yt_id = row['yt_id']

            # 清理名字
            filename = sanitize_filename(name)
            output_file = os.path.join(save_dir, filename + '.mp4')

            if os.path.exists(output_file):
                print(f"⏩ Skipping {filename}, already exists.")
                continue

            url = f"https://www.youtube.com/watch?v={yt_id}"
            download_video(url, save_path=save_dir, filename=filename)

# ==== 主程序 ====

if __name__ == "__main__":
    download_all_from_csv(CSV_PATH, SAVE_DIR)