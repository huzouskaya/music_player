import requests
import re
from typing import Optional

class GeniusLyrics:
    def __init__(self):
        self.base_url = "https://api.genius.com"
        # Note: For production use, you should get an API token from Genius
        # self.access_token = "your_access_token_here"

    def search_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Поиск текста по артисту и названию"""
        try:
            # Try direct URL construction first (more reliable)
            formatted_artist = artist.lower().replace(' ', '-').replace('&', 'and')
            formatted_title = title.lower().replace(' ', '-').replace('&', 'and')
            song_url = f"https://genius.com/{formatted_artist}-{formatted_title}-lyrics"

            lyrics = self.get_lyrics_from_url(song_url)
            if lyrics:
                return lyrics

            # Fallback to search API (requires token for full functionality)
            search_url = "https://api.genius.com/search"
            params = {'q': f"{artist} {title}"}
            headers = {
                'Authorization': f'Bearer {getattr(self, "access_token", "")}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(search_url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                hits = data.get('response', {}).get('hits', [])

                if hits:
                    song = hits[0]['result']
                    song_url = song['url']

                    return self.get_lyrics_from_url(song_url)

            return None

        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return None
    
    def get_lyrics_from_url(self, url: str) -> Optional[str]:
        """Получение текста по URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                html = response.text
                start = html.find('"lyricsContents-')
                if start != -1:
                    start = html.find('>', start) + 1
                    end = html.find('</div>', start)
                    lyrics_html = html[start:end]
                    
                    lyrics = re.sub(r'<[^>]+>', '', lyrics_html)
                    lyrics = re.sub(r'\[.*?\]', '\n', lyrics)
                    lyrics = lyrics.replace('\\n', '\n')
                    
                    return lyrics.strip()
            return None
        except:
            return None