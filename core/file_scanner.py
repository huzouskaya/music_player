import os
from pathlib import Path
from typing import Dict, List

class FileScanner:
    def __init__(self):
        self.audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff'}
    
    def scan_by_extensions(self, extensions: List[str]) -> Dict[str, List[str]]:
        result = {}

        scan_paths = [
            Path.home() / "Music",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.cwd(),
            Path.cwd() / "music",
            Path.cwd() / "audio"
        ]

        for scan_path in scan_paths:
            if not scan_path.exists():
                continue

            for root, dirs, files in os.walk(scan_path):
                for file in files:
                    if Path(file).suffix.lower() in extensions:
                        full_path = os.path.join(root, file)
                        ext = Path(file).suffix.lower()

                        if ext not in result:
                            result[ext] = []
                        result[ext].append(full_path)

        return result
