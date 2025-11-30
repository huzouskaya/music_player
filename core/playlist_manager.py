import json
import os
from pathlib import Path
from typing import List, Dict, Any

class PlaylistManager:
    def __init__(self, playlists_dir: str = "data/playlists"):
        self.playlists_dir = Path(playlists_dir)
        self.playlists_dir.mkdir(parents=True, exist_ok=True)
    
    def create_playlist(self, name: str, tracks: List[str] = None) -> bool:
        """Создание нового плейлиста"""
        if tracks is None:
            tracks = []

        playlist_data = {
            'name': name,
            'tracks': tracks
        }

        try:
            return self._extracted_from_update_playlist_12(name, playlist_data)
        except Exception as e:
            print(f"Ошибка создания плейлиста: {e}")
            return False
    
    def get_playlist(self, name: str) -> Dict[str, Any]:
        """Получение плейлиста"""
        try:
            playlist_path = self.playlists_dir / f"{name}.json"
            with open(playlist_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки плейлиста: {e}")
            return {}
    
    def add_to_playlist(self, playlist_name: str, track_path: str) -> bool:
        """Добавление трека в плейлист"""
        playlist = self.get_playlist(playlist_name)
        if not playlist:
            return False
        
        if track_path not in playlist['tracks']:
            playlist['tracks'].append(track_path)
            return self.update_playlist(playlist_name, playlist['tracks'])
        
        return True
    
    def update_playlist(self, playlist_name: str, tracks: List[str]) -> bool:
        """Обновление плейлиста"""
        playlist_data = {
            'name': playlist_name,
            'tracks': tracks
        }

        try:
            return self._extracted_from_update_playlist_12(playlist_name, playlist_data)
        except Exception as e:
            print(f"Ошибка обновления плейлиста: {e}")
            return False

    # TODO Rename this here and in `create_playlist` and `update_playlist`
    def _extracted_from_update_playlist_12(self, arg0, playlist_data):
        playlist_path = self.playlists_dir / f"{arg0}.json"
        with open(playlist_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, ensure_ascii=False, indent=2)
        return True
    
    def get_all_playlists(self) -> List[str]:
        """Получение всех плейлистов"""
        playlists = []
        playlists.extend(file.stem for file in self.playlists_dir.glob("*.json"))
        return playlists
    
    def delete_playlist(self, name: str) -> bool:
        """Удаление плейлиста"""
        try:
            playlist_path = self.playlists_dir / f"{name}.json"
            if playlist_path.exists():
                playlist_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления плейлиста: {e}")
            return False