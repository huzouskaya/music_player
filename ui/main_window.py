import os
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout,
                            QPushButton, QListWidget, QSlider, QLabel,
                            QWidget, QMessageBox, QTextEdit, QLineEdit, QFormLayout,
                            QListWidgetItem, QMenu, QAction,
                            QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.player import MusicPlayer
from core.playlist_manager import PlaylistManager
from core.metadata_editor import MetadataEditor
from core.lyrics_manager import LyricsManager
from core.file_scanner import FileScanner
from auth.payment_verifier import PaymentVerifier
from ui.subscription_dialog import SubscriptionDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.player = MusicPlayer()
        self.playlist_manager = PlaylistManager()
        self.metadata_editor = MetadataEditor()
        self.lyrics_manager = LyricsManager()
        self.scanner = FileScanner()

        self.current_track = None
        self._slider_pressed = False
        self.metadata_visible = False
        self.lyrics_visible = False
        
        self.load_icons()
        self.setup_ui()
        self.setup_timer()
        self.setup_player_connections()
        
    def load_icons(self):
        self.prev_icon = QIcon("ui/icons/previous.png")
        self.play_icon = QIcon("ui/icons/play.png")
        self.pause_icon = QIcon("ui/icons/pause.png") 
        self.stop_icon = QIcon("ui/icons/stop.png")
        self.next_icon = QIcon("ui/icons/next.png")
    
    def setup_player_connections(self):
        if hasattr(self.player, 'finished'):
            self.player.finished.connect(self.on_track_finished)
    
    def on_track_finished(self):
        self.next_track()
    
    def setup_ui(self):
        self.setWindowTitle("Музыкальный Плеер")
        self.setGeometry(100, 100, 1200, 800)

        self.statusBar().showMessage("Готов")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        central_panel = self.create_central_panel()
        main_layout.addWidget(central_panel, 2)
    
    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        scan_layout = QHBoxLayout()
        
        self.scan_mp3_btn = QPushButton("MP3")
        self.scan_mp3_btn.clicked.connect(lambda: self.scan_files(['.mp3']))
        scan_layout.addWidget(self.scan_mp3_btn)
        
        self.scan_wav_btn = QPushButton("WAV")
        self.scan_wav_btn.clicked.connect(lambda: self.scan_files(['.wav']))
        scan_layout.addWidget(self.scan_wav_btn)
        
        self.scan_ogg_btn = QPushButton("OGG")
        self.scan_ogg_btn.clicked.connect(lambda: self.scan_files(['.ogg']))
        scan_layout.addWidget(self.scan_ogg_btn)
        
        self.scan_all_btn = QPushButton("Все")
        self.scan_all_btn.clicked.connect(self.scan_all_files)
        scan_layout.addWidget(self.scan_all_btn)
        
        layout.addLayout(scan_layout)
        
        self.files_list = QListWidget()
        self.files_list.itemClicked.connect(self.play_selected_track)
        self.files_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.files_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(QLabel("Файлы:"))
        layout.addWidget(self.files_list)
        
        playlist_btn_layout = QHBoxLayout()
        create_playlist_btn = QPushButton("Создать плейлист")
        create_playlist_btn.clicked.connect(self.create_playlist_dialog)
        playlist_btn_layout.addWidget(create_playlist_btn)
        
        load_playlist_btn = QPushButton("Загрузить плейлист")
        load_playlist_btn.clicked.connect(self.load_playlist_dialog)
        playlist_btn_layout.addWidget(load_playlist_btn)
        
        layout.addLayout(playlist_btn_layout)
        
        self.playlists_list = QListWidget()
        self.playlists_list.itemDoubleClicked.connect(self.load_playlist)
        self.playlists_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlists_list.customContextMenuRequested.connect(self.show_playlist_context_menu)
        self.refresh_playlists()
        layout.addWidget(QLabel("Плейлисты:"))
        layout.addWidget(self.playlists_list)
        
        return panel
    
    def create_central_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        track_info_group = QGroupBox("Сейчас играет")
        track_info_layout = QVBoxLayout(track_info_group)
        
        self.track_info = QLabel("Трек не выбран")
        self.track_info.setStyleSheet("font-size: 32px; font-weight: bold; padding: 15px;")
        self.track_info.setAlignment(Qt.AlignCenter)
        track_info_layout.addWidget(self.track_info)
        
        layout.addWidget(track_info_group)
        
        progress_group = QGroupBox()
        progress_layout = QVBoxLayout(progress_group)
        
        time_layout = QHBoxLayout()
        self.position_label = QLabel("0:00")
        self.position_label.setStyleSheet("font-size: 14px;")
        self.duration_label = QLabel("0:00")
        self.duration_label.setStyleSheet("font-size: 14px;")
        
        time_layout.addWidget(self.position_label)
        time_layout.addStretch()
        time_layout.addWidget(self.duration_label)
        progress_layout.addLayout(time_layout)
        
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 12px;
                background: #ddd;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #0078d7;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -4px 0;
            }
        """)
        self.progress_slider.sliderMoved.connect(self.on_slider_move)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        progress_layout.addWidget(self.progress_slider)
        
        layout.addWidget(progress_group)
        
        control_group = QGroupBox("Управление")
        control_layout = QHBoxLayout(control_group)
        
        button_style = """
        QPushButton {
            font-size: 20px;
            padding: 15px 20px;
            border: 2px solid #555;
            border-radius: 8px;
            background-color: #444;
            color: white;
            min-width: 80px;
            min-height: 60px;
        }
        QPushButton:hover {
            background-color: #555;
            border-color: #666;
        }
        QPushButton:pressed {
            background-color: #333;
        }
        """
        
        button_size = QSize(100, 100)
        icon_size = QSize(32, 32)

        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(self.prev_icon)
        self.prev_btn.setIconSize(icon_size)
        self.prev_btn.setFixedSize(button_size)
        self.prev_btn.clicked.connect(self.previous_track)
        self.prev_btn.setToolTip("Предыдущий трек")

        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.play_icon)
        self.play_btn.setIconSize(icon_size)
        self.play_btn.setFixedSize(button_size)
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setToolTip("Воспроизвести/Пауза")

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.stop_icon)
        self.stop_btn.setIconSize(icon_size)
        self.stop_btn.setFixedSize(button_size)
        self.stop_btn.clicked.connect(self.player.stop)
        self.stop_btn.setToolTip("Стоп")

        self.next_btn = QPushButton()
        self.next_btn.setIcon(self.next_icon)
        self.next_btn.setIconSize(icon_size)
        self.next_btn.setFixedSize(button_size)
        self.next_btn.clicked.connect(self.next_track)
        self.next_btn.setToolTip("Следующий трек")
        
        control_layout.addWidget(self.prev_btn)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.stop_btn) 
        control_layout.addWidget(self.next_btn)
        
        layout.addWidget(control_group)
        
        volume_group = QGroupBox("Громкость")
        volume_layout = QHBoxLayout(volume_group)
        
        volume_layout.addWidget(QLabel("🔊"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        self.volume_label = QLabel("50%")
        volume_layout.addWidget(self.volume_label)
        
        layout.addWidget(volume_group)
        
        info_buttons_layout = QHBoxLayout()
        
        self.metadata_btn = QPushButton("📝 Метаданные")
        self.metadata_btn.setCheckable(True)
        self.metadata_btn.clicked.connect(self.toggle_metadata)
        info_buttons_layout.addWidget(self.metadata_btn)
        
        self.lyrics_btn = QPushButton("🎵 Текст песни")
        self.lyrics_btn.setCheckable(True)
        self.lyrics_btn.clicked.connect(self.toggle_lyrics)
        info_buttons_layout.addWidget(self.lyrics_btn)
        
        layout.addLayout(info_buttons_layout)
        
        self.metadata_area = QGroupBox("Метаданные")
        self.metadata_area.setVisible(False)
        metadata_layout = QVBoxLayout(self.metadata_area)
        
        metadata_form = self.create_metadata_form()
        metadata_layout.addWidget(metadata_form)
        
        layout.addWidget(self.metadata_area)
        
        self.lyrics_area = QGroupBox("Текст песни")
        self.lyrics_area.setVisible(False)
        lyrics_layout = QVBoxLayout(self.lyrics_area)
        
        lyrics_form = self.create_lyrics_form()
        lyrics_layout.addWidget(lyrics_form)
        
        layout.addWidget(self.lyrics_area)
        
        return panel
    
    def create_metadata_form(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.metadata_title = QLineEdit()
        self.metadata_artist = QLineEdit()
        self.metadata_album = QLineEdit()
        self.metadata_year = QLineEdit()
        self.metadata_genre = QLineEdit()
        self.metadata_comment = QTextEdit()
        self.metadata_comment.setMaximumHeight(80)
        
        layout.addRow("Название:", self.metadata_title)
        layout.addRow("Исполнитель:", self.metadata_artist)
        layout.addRow("Альбом:", self.metadata_album)
        layout.addRow("Год:", self.metadata_year)
        layout.addRow("Жанр:", self.metadata_genre)
        layout.addRow("Комментарий:", self.metadata_comment)
        
        save_btn = QPushButton("Сохранить метаданные")
        save_btn.clicked.connect(self.save_metadata)
        layout.addRow(save_btn)
        
        return widget
    
    def create_lyrics_form(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.lyrics_text = QTextEdit()
        layout.addWidget(self.lyrics_text)
        
        btn_layout = QHBoxLayout()
        
        genius_btn = QPushButton("Найти на Genius")
        genius_btn.clicked.connect(self.search_genius_lyrics)
        btn_layout.addWidget(genius_btn)
        
        save_btn = QPushButton("Сохранить текст")
        save_btn.clicked.connect(self.save_lyrics)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def toggle_metadata(self):
        self.metadata_visible = not self.metadata_visible
        self.metadata_area.setVisible(self.metadata_visible)
        self.metadata_btn.setChecked(self.metadata_visible)
    
    def toggle_lyrics(self):
        self.lyrics_visible = not self.lyrics_visible
        self.lyrics_area.setVisible(self.lyrics_visible)
        self.lyrics_btn.setChecked(self.lyrics_visible)
    
    def get_display_name(self, file_path):
        metadata = self.metadata_editor.get_metadata(file_path)
        title = metadata.get('title', '').strip()
        artist = metadata.get('artist', '').strip()
        
        if title and artist:
            return f"{title} - {artist}"
        elif title:
            return title
        elif artist:
            return f"Неизвестно - {artist}"
        else:
            return os.path.splitext(os.path.basename(file_path))[0]
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)
    
    def scan_files(self, extensions):
        self.files_list.clear()
        self.statusBar().showMessage(f"Сканирую {extensions}...")

        try:
            self._extracted_from_scan_files_7(extensions)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка сканирования: {str(e)}")

    def _extracted_from_scan_files_7(self, extensions):
        files_by_ext = self.scanner.scan_by_extensions(extensions)
        all_files = []
        for ext_files in files_by_ext.values():
            all_files.extend(ext_files)

        for file_path in all_files:
            display_name = self.get_display_name(file_path)
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, file_path)
            self.files_list.addItem(item)

        self.player.current_playlist = all_files
        self.statusBar().showMessage(f"Найдено {len(all_files)} файлов")
    
    def scan_all_files(self):
        self.scan_files(['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'])
    
    def play_selected_track(self, item):
        if not item:
            return
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self._extracted_from_play_selected_track_5(file_path)
        self.highlight_current_track()

    def _extracted_from_play_selected_track_5(self, file_path):
        if file_path in self.player.current_playlist:
            self.player.current_index = self.player.current_playlist.index(file_path)

        self.player.play(file_path)
        self.current_track = file_path
        self.load_track_info()
        self.play_btn.setIcon(self.pause_icon)
        self.play_btn.setToolTip("Пауза")

    def next_track(self):
        self.player.next_track()
        if self.player.current_playlist:
            self.current_track = self.player.current_playlist[self.player.current_index]
            self.load_track_info()
            self.play_btn.setIcon(self.pause_icon)
            self.play_btn.setToolTip("Пауза")
        self.highlight_current_track()

    def previous_track(self):
        self.player.previous_track()
        if self.player.current_playlist:
            self.current_track = self.player.current_playlist[self.player.current_index]
            self.load_track_info()
            self.play_btn.setIcon(self.pause_icon)
            self.play_btn.setToolTip("Пауза")
        self.highlight_current_track()
        
    def highlight_current_track(self):
        if self.player.current_playlist and self.player.current_index >= 0:
            for i in range(self.files_list.count()):
                item = self.files_list.item(i)
                file_path = item.data(Qt.UserRole)
                if file_path == self.current_track:
                    self.files_list.setCurrentRow(i)
                    break
    
    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            icon = self.play_icon
            tooltip = "Воспроизвести"
        else:
            self.player.play()
            icon = self.pause_icon
            tooltip = "Пауза"
        
        self.play_btn.setIcon(icon)
        self.play_btn.setToolTip(tooltip)
            
    def search_genius_lyrics(self):
        verifier = PaymentVerifier()
        if not verifier.verify_license():
            dialog = SubscriptionDialog(self)
            dialog.exec()
            # Check again after dialog closes
            if not verifier.verify_license():
                return

        metadata = self.metadata_editor.get_metadata(self.current_track) if self.current_track else {}

        artist = metadata.get('artist', '')
        title = metadata.get('title', '')

        if not title and self.current_track:
            title = os.path.splitext(os.path.basename(self.current_track))[0]

        from PyQt5.QtWidgets import QDialog, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Поиск текста на Genius")
        layout = QVBoxLayout(dialog)

        artist_edit = self._extracted_from_search_genius_lyrics_17(layout, "Исполнитель:", artist)
        title_edit = self._extracted_from_search_genius_lyrics_17(layout, "Название песни:", title)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            artist = artist_edit.text().strip()
            title = title_edit.text().strip()

            if not title:
                QMessageBox.warning(self, "Ошибка", "Введите название песни")
                return

            self.statusBar().showMessage("Ищем текст на Genius...")
            lyrics_text = self.lyrics_manager.search_genius(artist, title)
            self.statusBar().showMessage("Поиск завершен")
            self.lyrics_text.setText(lyrics_text)

            if "не найден" in lyrics_text or "Ошибка" in lyrics_text:
                QMessageBox.information(self, "Результат", lyrics_text)
            else:
                QMessageBox.information(self, "Успех", "Текст найден на Genius!")

    def _extracted_from_search_genius_lyrics_17(self, layout, arg1, arg2):
        layout.addWidget(QLabel(arg1))
        result = QLineEdit(arg2)
        layout.addWidget(result)
        return result
    
    def set_volume(self, value):
        if value == 0:
            volume = 0
        else:
            volume = int((value / 100.0) ** 1.5 * 100)
            volume = min(100, max(0, volume))
        
        self.player.set_volume(volume)
        self.volume_label.setText(f"{value}%")
    
    def on_slider_move(self, position):
        if not self._slider_pressed:
            self.player.set_position(position / 1000.0)
    
    def slider_pressed(self):
        self._slider_pressed = True
    
    def slider_released(self):
        self._slider_pressed = False
        position = self.progress_slider.value()
        self.player.set_position(position / 1000.0)
    
    def update_display(self):
        if self.player.is_playing():
            length = self.player.get_length()
            position = self.player.get_position()
            
            if length > 0 and not self._slider_pressed:
                self.progress_slider.setValue(int(position * 1000))
                
                current_sec = int(position * length / 1000)
                total_sec = int(length / 1000)
                
                self.position_label.setText(f"{current_sec//60}:{current_sec%60:02d}")
                self.duration_label.setText(f"{total_sec//60}:{total_sec%60:02d}")
            
            if position >= 0.999:
                self.next_track()
    
    def load_track_info(self):
        if self.current_track:
            display_name = self.get_display_name(self.current_track)
            self.track_info.setText(display_name)
            
            metadata = self.metadata_editor.get_metadata(self.current_track)
            self.metadata_title.setText(metadata.get('title', ''))
            self.metadata_artist.setText(metadata.get('artist', ''))
            self.metadata_album.setText(metadata.get('album', ''))
            self.metadata_year.setText(metadata.get('year', ''))
            self.metadata_genre.setText(metadata.get('genre', ''))
            self.metadata_comment.setText(metadata.get('comment', ''))
            
            lyrics = self.lyrics_manager.load_lyrics(self.current_track)
            self.lyrics_text.setText(lyrics.get('original', ''))
    
    def save_metadata(self):
        verifier = PaymentVerifier()
        if not verifier.verify_license():
            dialog = SubscriptionDialog(self)
            dialog.exec()
            # Check again after dialog closes
            if not verifier.verify_license():
                return

        if not self.current_track:
            return
        metadata = {
            'title': self.metadata_title.text(),
            'artist': self.metadata_artist.text(),
            'album': self.metadata_album.text(),
            'year': self.metadata_year.text(),
            'genre': self.metadata_genre.text(),
            'comment': self.metadata_comment.toPlainText()
        }

        if self.metadata_editor.set_metadata(self.current_track, metadata):
            self.load_track_info()
            for i in range(self.files_list.count()):
                item = self.files_list.item(i)
                if item.data(Qt.UserRole) == self.current_track:
                    item.setText(self.get_display_name(self.current_track))
                    break
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить метаданные")
    
    def save_lyrics(self):
        if self.current_track:
            lyrics_data = {
                'original': self.lyrics_text.toPlainText(),
                'translation': '',
                'auto_translated': False
            }
            
            if not self.lyrics_manager.save_lyrics(self.current_track, lyrics_data):
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить текст")
    
    
    def recognize_lyrics(self):
        if self.current_track:
            try:
                lyrics_data = self.lyrics_manager.extract_lyrics_from_audio(self.current_track)
                if lyrics_data.get('original'):
                    self.lyrics_text.setText(lyrics_data['original'])
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось распознать текст")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка распознавания: {str(e)}")
    
    def create_playlist_dialog(self):
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Создать плейлист", "Введите название:")
        if ok and name:
            if self.playlist_manager.create_playlist(name):
                self.refresh_playlists()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось создать плейлист")
    
    def load_playlist_dialog(self):
        from PyQt5.QtWidgets import QInputDialog
        playlists = self.playlist_manager.get_all_playlists()
        if not playlists:
            QMessageBox.information(self, "Информация", "Нет доступных плейлистов")
            return
        
        name, ok = QInputDialog.getItem(self, "Загрузить плейлист", "Выберите плейлист:", playlists, 0, False)
        if ok and name:
            self.load_playlist_by_name(name)
    
    def load_playlist_by_name(self, name):
        if playlist_data := self.playlist_manager.get_playlist(name):
            self.player.current_playlist = playlist_data.get('tracks', [])
            self.files_list.clear()
            for track in self.player.current_playlist:
                item = QListWidgetItem(os.path.basename(track))
                item.setData(Qt.UserRole, track)
                self.files_list.addItem(item)
            self.statusBar().showMessage(f"Загружен плейлист: {name}")
    
    def load_playlist(self, item):
        if item:
            self.load_playlist_by_name(item.text())
    
    def refresh_playlists(self):
        self.playlists_list.clear()
        playlists = self.playlist_manager.get_all_playlists()
        self.playlists_list.addItems(playlists)

    def show_context_menu(self, position):
        item = self.files_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        if playlists := self.playlist_manager.get_all_playlists():
            for playlist_name in playlists:
                action = QAction(f"Добавить в '{playlist_name}'", self)
                action.triggered.connect(lambda checked, name=playlist_name: self.add_to_playlist(name, item))
                menu.addAction(action)

        else:
            no_playlist_action = QAction("Нет доступных плейлистов", self)
            no_playlist_action.setEnabled(False)
            menu.addAction(no_playlist_action)
        menu.exec_(self.files_list.mapToGlobal(position))

    def add_to_playlist(self, playlist_name, item):
        file_path = item.data(Qt.UserRole)
        if not file_path or not self.playlist_manager.add_to_playlist(
            playlist_name, file_path
        ):
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить трек в плейлист")

    def show_playlist_context_menu(self, position):
        item = self.playlists_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        delete_action = QAction("Удалить плейлист", self)
        delete_action.triggered.connect(lambda: self.delete_playlist(item.text()))
        menu.addAction(delete_action)

        menu.exec_(self.playlists_list.mapToGlobal(position))

    def delete_playlist(self, playlist_name):
        reply = QMessageBox.question(self, "Подтверждение",
                                   f"Вы действительно хотите удалить плейлист '{playlist_name}'?",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.playlist_manager.delete_playlist(playlist_name):
                self.refresh_playlists()
                QMessageBox.information(self, "Успех", f"Плейлист '{playlist_name}' удален")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить плейлист")
