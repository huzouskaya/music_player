import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, COMM, TPE2, TCOM, TXXX, USLT, APIC
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
import os
from typing import Dict, Any

class MetadataEditor:
    def __init__(self):
        self.supported_formats = {'.mp3', '.flac', '.m4a', '.aac'}
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Получение метаданных трека"""
        try:
            audio_file = mutagen.File(file_path, easy=False)  # Используем easy=False для полных тегов
            if audio_file is None:
                return {}
            
            metadata = {}
            
            if hasattr(audio_file, 'tags'):
                if file_path.lower().endswith('.mp3'):
                    metadata = self._get_id3_metadata(audio_file)
                elif file_path.lower().endswith('.flac'):
                    metadata = self._get_flac_metadata(audio_file)
                elif file_path.lower().endswith(('.m4a', '.aac')):
                    metadata = self._get_mp4_metadata(audio_file)
            
            # Добавляем техническую информацию
            if hasattr(audio_file, 'info'):
                metadata['length'] = audio_file.info.length
                metadata['bitrate'] = getattr(audio_file.info, 'bitrate', 0)
                metadata['sample_rate'] = getattr(audio_file.info, 'sample_rate', 0)
                metadata['channels'] = getattr(audio_file.info, 'channels', 0)
            
            return metadata
            
        except Exception as e:
            print(f"Ошибка чтения метаданных: {e}")
            return {}
    
    def _get_id3_metadata(self, audio_file) -> Dict[str, Any]:
        """Получение ID3 метаданных"""
        metadata = {}
        tags = audio_file.tags
        
        if not tags:
            return metadata
            
        # Основные теги
        metadata['title'] = self._get_tag_value(tags, 'TIT2')
        metadata['artist'] = self._get_tag_value(tags, 'TPE1')
        metadata['album'] = self._get_tag_value(tags, 'TALB')
        metadata['album_artist'] = self._get_tag_value(tags, 'TPE2')
        metadata['composer'] = self._get_tag_value(tags, 'TCOM')
        
        # Дата/год - пробуем разные теги
        metadata['year'] = self._get_tag_value(tags, 'TDRC') or self._get_tag_value(tags, 'TYER')
        metadata['date'] = metadata['year']
        
        metadata['genre'] = self._get_tag_value(tags, 'TCON')
        metadata['comment'] = self._get_tag_value(tags, 'COMM')
        
        # Дополнительные теги
        metadata['track_number'] = self._get_track_number(tags)
        metadata['disc_number'] = self._get_disc_number(tags)
        
        return metadata
    
    def _get_flac_metadata(self, audio_file) -> Dict[str, Any]:
        """Получение FLAC метаданных"""
        metadata = {}
        tags = audio_file.tags
        
        if not tags:
            return metadata
            
        # Vorbis comments для FLAC
        metadata['title'] = tags.get('title', [''])[0] if tags.get('title') else ''
        metadata['artist'] = tags.get('artist', [''])[0] if tags.get('artist') else ''
        metadata['album'] = tags.get('album', [''])[0] if tags.get('album') else ''
        metadata['album_artist'] = tags.get('albumartist', [''])[0] if tags.get('albumartist') else ''
        metadata['composer'] = tags.get('composer', [''])[0] if tags.get('composer') else ''
        metadata['year'] = tags.get('date', [''])[0] if tags.get('date') else ''
        metadata['date'] = metadata['year']
        metadata['genre'] = tags.get('genre', [''])[0] if tags.get('genre') else ''
        metadata['comment'] = tags.get('comment', [''])[0] if tags.get('comment') else ''
        metadata['track_number'] = tags.get('tracknumber', [''])[0] if tags.get('tracknumber') else ''
        metadata['disc_number'] = tags.get('discnumber', [''])[0] if tags.get('discnumber') else ''
        
        return metadata
    
    def _get_mp4_metadata(self, audio_file) -> Dict[str, Any]:
        """Получение MP4 метаданных"""
        metadata = {}
        tags = audio_file.tags
        
        if not tags:
            return metadata
            
        # iTunes-style tags для MP4
        metadata['title'] = tags.get('\xa9nam', [''])[0] if tags.get('\xa9nam') else ''
        metadata['artist'] = tags.get('\xa9ART', [''])[0] if tags.get('\xa9ART') else ''
        metadata['album'] = tags.get('\xa9alb', [''])[0] if tags.get('\xa9alb') else ''
        metadata['album_artist'] = tags.get('aART', [''])[0] if tags.get('aART') else ''
        metadata['composer'] = tags.get('\xa9wrt', [''])[0] if tags.get('\xa9wrt') else ''
        metadata['year'] = tags.get('\xa9day', [''])[0] if tags.get('\xa9day') else ''
        metadata['date'] = metadata['year']
        metadata['genre'] = tags.get('\xa9gen', [''])[0] if tags.get('\xa9gen') else ''
        metadata['comment'] = tags.get('\xa9cmt', [''])[0] if tags.get('\xa9cmt') else ''
        
        # Номер трека и диска
        trkn = tags.get('trkn')
        if trkn:
            metadata['track_number'] = f"{trkn[0][0]}/{trkn[0][1]}" if trkn[0][1] else str(trkn[0][0])
        
        disk = tags.get('disk')
        if disk:
            metadata['disc_number'] = f"{disk[0][0]}/{disk[0][1]}" if disk[0][1] else str(disk[0][0])
        
        return metadata
    
    def _get_tag_value(self, tags, tag_name):
        """Безопасное получение значения тега"""
        try:
            return str(tags[tag_name][0]) if tag_name in tags else ''
        except:
            return ''
    
    def _get_track_number(self, tags):
        """Получение номера трека"""
        try:
            if 'TRCK' in tags:
                return str(tags['TRCK'][0])
            return ''
        except:
            return ''
    
    def _get_disc_number(self, tags):
        """Получение номера диска"""
        try:
            if 'TPOS' in tags:
                return str(tags['TPOS'][0])
            return ''
        except:
            return ''
    
    def set_metadata(self, file_path: str, metadata: Dict[str, str]) -> bool:
        """Установка метаданных трека"""
        try:
            if not os.path.exists(file_path):
                print(f"Файл не существует: {file_path}")
                return False

            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.mp3':
                return self._set_id3_metadata(file_path, metadata)
            elif file_ext == '.flac':
                return self._set_flac_metadata(file_path, metadata)
            elif file_ext in ('.m4a', '.aac'):
                return self._set_mp4_metadata(file_path, metadata)
            else:
                print(f"Неподдерживаемый формат: {file_ext}")
                return False

        except Exception as e:
            print(f"Ошибка записи метаданных: {e}")
            return False
    
    def _set_id3_metadata(self, file_path: str, metadata: Dict[str, str]) -> bool:
        """Установка ID3 метаданных"""
        try:
            # Загружаем или создаем новые теги
            try:
                tags = ID3(file_path)
            except:
                tags = ID3()
            
            # Кодировка 3 = UTF-8
            encoding = 3
            
            if metadata.get('title'):
                tags['TIT2'] = TIT2(encoding=encoding, text=metadata['title'])
            if metadata.get('artist'):
                tags['TPE1'] = TPE1(encoding=encoding, text=metadata['artist'])
            if metadata.get('album'):
                tags['TALB'] = TALB(encoding=encoding, text=metadata['album'])
            if metadata.get('album_artist'):
                tags['TPE2'] = TPE2(encoding=encoding, text=metadata['album_artist'])
            if metadata.get('composer'):
                tags['TCOM'] = TCOM(encoding=encoding, text=metadata['composer'])
            if metadata.get('year'):
                tags['TDRC'] = TDRC(encoding=encoding, text=metadata['year'])
            if metadata.get('genre'):
                tags['TCON'] = TCON(encoding=encoding, text=metadata['genre'])
            if metadata.get('comment'):
                tags['COMM'] = COMM(encoding=encoding, text=metadata['comment'])
            
            # Номер трека и диска
            if metadata.get('track_number'):
                tags['TRCK'] = mutagen.id3.TRCK(encoding=encoding, text=metadata['track_number'])
            if metadata.get('disc_number'):
                tags['TPOS'] = mutagen.id3.TPOS(encoding=encoding, text=metadata['disc_number'])
            
            # Сохраняем теги
            tags.save(file_path)
            print(f"Метаданные успешно сохранены для {file_path}")
            return True
            
        except Exception as e:
            print(f"Ошибка записи ID3: {e}")
            return False

    def _set_flac_metadata(self, file_path: str, metadata: Dict[str, str]) -> bool:
        """Установка FLAC метаданных"""
        try:
            audio = FLAC(file_path)
            
            # Очищаем старые теги перед установкой новых
            audio.delete()
            
            if metadata.get('title'):
                audio['title'] = metadata['title']
            if metadata.get('artist'):
                audio['artist'] = metadata['artist']
            if metadata.get('album'):
                audio['album'] = metadata['album']
            if metadata.get('album_artist'):
                audio['albumartist'] = metadata['album_artist']
            if metadata.get('composer'):
                audio['composer'] = metadata['composer']
            if metadata.get('year'):
                audio['date'] = metadata['year']
            if metadata.get('genre'):
                audio['genre'] = metadata['genre']
            if metadata.get('comment'):
                audio['comment'] = metadata['comment']
            if metadata.get('track_number'):
                audio['tracknumber'] = metadata['track_number']
            if metadata.get('disc_number'):
                audio['discnumber'] = metadata['disc_number']
            
            audio.save()
            print(f"Метаданные успешно сохранены для {file_path}")
            return True

        except Exception as e:
            print(f"Ошибка записи FLAC: {e}")
            return False

    def _set_mp4_metadata(self, file_path: str, metadata: Dict[str, str]) -> bool:
        """Установка MP4 метаданных"""
        try:
            audio = MP4(file_path)
            
            # Очищаем старые теги
            audio.clear()
            
            if metadata.get('title'):
                audio['\xa9nam'] = metadata['title']
            if metadata.get('artist'):
                audio['\xa9ART'] = metadata['artist']
            if metadata.get('album'):
                audio['\xa9alb'] = metadata['album']
            if metadata.get('album_artist'):
                audio['aART'] = metadata['album_artist']
            if metadata.get('composer'):
                audio['\xa9wrt'] = metadata['composer']
            if metadata.get('year'):
                audio['\xa9day'] = metadata['year']
            if metadata.get('genre'):
                audio['\xa9gen'] = metadata['genre']
            if metadata.get('comment'):
                audio['\xa9cmt'] = metadata['comment']
            
            # Номер трека и диска
            if metadata.get('track_number'):
                try:
                    track_num = int(metadata['track_number'].split('/')[0])
                    audio['trkn'] = [(track_num, 0)]
                except:
                    pass
            
            if metadata.get('disc_number'):
                try:
                    disc_num = int(metadata['disc_number'].split('/')[0])
                    audio['disk'] = [(disc_num, 0)]
                except:
                    pass
            
            audio.save()
            print(f"Метаданные успешно сохранены для {file_path}")
            return True

        except Exception as e:
            print(f"Ошибка записи MP4: {e}")
            return False

    def get_supported_formats(self):
        """Получить список поддерживаемых форматов"""
        return self.supported_formats

# Пример использования
if __name__ == "__main__":
    editor = MetadataEditor()
    
    # Пример чтения метаданных
    metadata = editor.get_metadata("example.mp3")
    print("Текущие метаданные:", metadata)
    
    # Пример записи метаданных
    new_metadata = {
        'title': 'Название трека',
        'artist': 'Исполнитель',
        'album': 'Альбом',
        'year': '2024',
        'genre': 'Rock',
        'comment': 'Комментарий',
        'track_number': '1'
    }
    
    success = editor.set_metadata("example.mp3", new_metadata)
    print(f"Запись метаданных: {'Успешно' if success else 'Ошибка'}")