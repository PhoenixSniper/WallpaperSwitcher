# main.p
import os
import json
import subprocess
from flowlauncher import FlowLauncher
from PIL import Image

# ⚠️ Change this to your Wallpaper Engine path
WALLPAPER_ENGINE_EXE = r"E:\SteamLibrary\steamapps\common\wallpaper_engine\wallpaper64.exe"

# Folders to scan
WALLPAPER_DIRS = [
    r"E:\SteamLibrary\steamapps\workshop\content\431960",  # Steam Workshop wallpapers
]

# Temp cache folder for converted previews
CACHE_DIR = os.path.expanduser("~/.wallpaper_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class WallpaperSwitcher(FlowLauncher):

    def query(self, query):
        results = []

        wallpapers = self.scan_wallpapers()

        for wp in wallpapers:
            if query.lower() in wp["name"].lower():
                results.append({
                    "Title": wp["name"],
                    # "SubTitle": wp["path"],
                    "IcoPath": wp["preview"] if os.path.exists(wp["preview"]) else "icon.png",
                    "JsonRPCAction": {
                        "method": "set_wallpaper",
                        "parameters": [wp["path"]],
                        "dontHideAfterAction": False
                    }
                })
        return results

    def scan_wallpapers(self):
        wallpapers = []
        for base_dir in WALLPAPER_DIRS:
            for root, dirs, files in os.walk(base_dir):
                if "project.json" in files:
                    pj_path = os.path.join(root, "project.json")
                    try:
                        with open(pj_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            name = data.get("title", os.path.basename(root))

                        # Find preview file
                        preview = None
                        for ext in ("jpg", "png", "gif"):
                            candidate = os.path.join(root, f"preview.{ext}")
                            if os.path.exists(candidate):
                                preview = candidate
                                break

                        if preview and preview.endswith(".gif"):
                            # Convert gif -> jpg once and store in cache
                            cache_file = os.path.join(
                                CACHE_DIR,
                                f"{os.path.basename(root)}.jpg"
                            )
                            if not os.path.exists(cache_file):
                                try:
                                    img = Image.open(preview)
                                    # Get middle frame
                                    total_frames = getattr(img, "n_frames", 1)
                                    middle_frame = total_frames // 2

                                    img.seek(middle_frame)  # move to middle frame
                                    img.convert("RGB").save(cache_file, "JPEG")
                                except Exception as e:
                                    print(f"GIF convert failed {preview}: {e}")
                                    cache_file = "icon.png"
                            preview = cache_file

                        wallpapers.append({
                            "name": name,
                            "path": pj_path,
                            "preview": preview or "icon.png"
                        })

                    except Exception as e:
                        print(f"Error reading {pj_path}: {e}")
        return wallpapers

    def set_wallpaper(self, pj_path):
        subprocess.Popen([
            WALLPAPER_ENGINE_EXE,
            "-control", "openWallpaper",
            "-file", pj_path,
            "-monitor", "0"
        ])

if __name__ == "__main__":
    WallpaperSwitcher()

