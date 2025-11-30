import os
import vlc
from pathlib import Path
from typing import List, Optional, Dict
import json

class MusicPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_playlist = []
        self.current_index = 0
        self.volume = 50
        self.player.audio_set_volume(self.volume)
        
    def load_folder(self, folder_path: str) -> List[str]:
        """Загрузка всех аудиофайлов из папки"""
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff'}
        audio_files = []

        for root, dirs, files in os.walk(folder_path):
            audio_files.extend(
                os.path.join(root, file)
                for file in files
                if Path(file).suffix.lower() in audio_extensions
            )
        self.current_playlist = audio_files
        return audio_files
    
    def load_playlist(self, playlist_path: str) -> List[str]:
        """Загрузка плейлиста из файла"""
        try:
            with open(playlist_path, 'r', encoding='utf-8') as f:
                playlist_data = json.load(f)
                self.current_playlist = playlist_data.get('tracks', [])
                return self.current_playlist
        except Exception as e:
            print(f"Ошибка загрузки плейлиста: {e}")
            return []
    
    def play(self, track_path: Optional[str] = None):
        """Воспроизведение трека"""
        if track_path:
            media = self.instance.media_new(track_path)
            self.player.set_media(media)
        
        self.player.play()
    
    def pause(self):
        """Пауза"""
        self.player.pause()
    
    def stop(self):
        """Остановка"""
        self.player.stop()
    
    def next_track(self):
        """Следующий трек"""
        if self.current_playlist and self.current_index < len(self.current_playlist) - 1:
            self.current_index += 1
            self.play(self.current_playlist[self.current_index])
    
    def previous_track(self):
        """Предыдущий трек"""
        if self.current_playlist and self.current_index > 0:
            self.current_index -= 1
            self.play(self.current_playlist[self.current_index])
    
    def set_volume(self, volume: int):
        """Установка громкости"""
        self.volume = max(0, min(100, volume))
        self.player.audio_set_volume(self.volume)
    
    def get_position(self) -> float:
        """Получение текущей позиции"""
        return self.player.get_position()
    
    def set_position(self, position: float):
        """Установка позиции"""
        self.player.set_position(max(0, min(1, position)))
    
    def get_length(self) -> int:
        """Получение длительности трека"""
        return self.player.get_length()
    
    def is_playing(self) -> bool:
        """Проверка воспроизведения"""
        return self.player.is_playing()