import os
from pathlib import Path
import subprocess
from typing import Optional

class AudioConverter:
    SUPPORTED_FORMATS = {
        'mp3': 'libmp3lame',
        'wav': 'pcm_s16le',
        'flac': 'flac',
        'ogg': 'libvorbis',
        'm4a': 'aac'
    }
    
    def __init__(self):
        self.check_ffmpeg()
    
    def check_ffmpeg(self):
        """Проверка наличия FFmpeg"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception("FFmpeg не найден. Установите FFmpeg для использования конвертера.")
    
    def convert_audio(self, input_path: str, output_format: str, 
                    output_dir: Optional[str] = None) -> Optional[str]:
        """Конвертация аудиофайла"""
        if output_format.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Формат {output_format} не поддерживается")
        
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Файл {input_path} не найден")
        
        if output_dir is None:
            output_dir = input_path.parent
        
        output_path = Path(output_dir) / f"{input_path.stem}.{output_format}"
        
        try:
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-c:a', self.SUPPORTED_FORMATS[output_format.lower()],
                '-y',
                str(output_path)
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            return str(output_path)
        
        except subprocess.CalledProcessError as e:
            print(f"Ошибка конвертации: {e}")
            return None