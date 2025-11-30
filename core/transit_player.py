import os
import vlc

class TransitPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_file = None
        
    def play_file(self, file_path: str):
        """Воспроизводит файл напрямую с диска"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        media = self.instance.media_new_path(file_path)
        self.player.set_media(media)
        self.player.play()
        self.current_file = file_path
    
    def get_current_position(self) -> float:
        return self.player.get_position()
    
    def set_position(self, position: float):
        self.player.set_position(position)
    
    def get_length(self) -> int:
        return self.player.get_length()