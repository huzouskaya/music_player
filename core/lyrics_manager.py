import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from core.genius_lyrics import GeniusLyrics

class LyricsManager:
    def __init__(self, lyrics_dir: str = "data/lyrics"):
        self.lyrics_dir = Path(lyrics_dir)
        self.lyrics_dir.mkdir(parents=True, exist_ok=True)
        self.genius = GeniusLyrics()
    
    def get_lyrics_path(self, track_path: str) -> Path:
        """Получение пути к файлу текста"""
        track_name = Path(track_path).stem
        return self.lyrics_dir / f"{track_name}.json"
    
    def load_lyrics(self, track_path: str) -> Dict[str, Any]:
        """Загрузка текста трека"""
        lyrics_path = self.get_lyrics_path(track_path)
        
        if lyrics_path.exists():
            try:
                with open(lyrics_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки текста: {e}")
        
        return {
            'original': '', 
            'translation': '', 
            'source': 'none',
            'auto_generated': False,
            'needs_review': True
        }
    
    def save_lyrics(self, track_path: str, lyrics_data: Dict[str, Any]) -> bool:
        """Сохранение текста трека"""
        try:
            lyrics_path = self.get_lyrics_path(track_path)
            with open(lyrics_path, 'w', encoding='utf-8') as f:
                json.dump(lyrics_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения текста: {e}")
            return False
    
    def search_genius(self, artist: str, title: str) -> str:
        """Поиск текста на Genius"""
        try:
            lyrics = self.genius.search_lyrics(artist, title)
            return lyrics or "Текст не найден на Genius"
        except Exception as e:
            return f"Ошибка поиска: {str(e)}"
    
    def auto_translate_lyrics(self, text: str, target_lang: str = 'ru') -> str:
        """Автоматический перевод текста (заглушка)"""
        # Можно добавить перевод через Google Translate API
        return f"[Перевод] {text}"