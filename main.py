# main.py
import os
import json
import subprocess
from flowlauncher import FlowLauncher

# ⚠️ Change this to your Wallpaper Engine path
WALLPAPER_ENGINE_EXE = r"E:\SteamLibrary\steamapps\common\wallpaper_engine\wallpaper64.exe"

# Folders to scan
WALLPAPER_DIRS = [
    r"E:\SteamLibrary\steamapps\workshop\content\431960",  # Steam Workshop wallpapers
]

class WallpaperSwitcher(FlowLauncher):

    def query(self, query):
        results = []

        wallpapers = self.scan_wallpapers()

        for wp in wallpapers:
            if query.lower() in wp["name"].lower():
                results.append({
                    "Title": wp["name"],
                    "SubTitle": wp["path"],
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
                            preview = os.path.join(root, "preview.jpg")
                            wallpapers.append({
                                "name": name,
                                "path": pj_path,
                                "preview": preview
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
