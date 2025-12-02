import os
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout,
                            QPushButton, QListWidget, QSlider, QLabel,
                            QWidget, QMessageBox, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer, QSize, QEvent
from PyQt5.QtGui import QIcon
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.player import MusicPlayer
from core.file_scanner import FileScanner
from ui.main_window import MainWindow
from ui.themes import ThemeManager

class MiniPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.player = MusicPlayer()
        self.scanner = FileScanner()
        self.current_track = None
        self._slider_pressed = False

        ThemeManager.load_theme_from_settings()
        
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
        self.setWindowTitle("Мини Плеер")
        self.setGeometry(100, 100, 400, 400)

        self.statusBar().showMessage("Готов")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        scan_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Сканировать MP3")
        self.scan_btn.clicked.connect(self.scan_mp3_files)
        scan_layout.addWidget(self.scan_btn)
        scan_layout.addStretch()
        main_layout.addLayout(scan_layout)

        self.files_list = QListWidget()
        self.files_list.itemClicked.connect(self.play_selected_track)
        main_layout.addWidget(QLabel("Треки:"))
        main_layout.addWidget(self.files_list)

        self.track_info = QLabel("Трек не выбран")
        self.track_info.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        self.track_info.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.track_info)

        progress_layout = QHBoxLayout()
        self.position_label = QLabel("0:00")
        progress_layout.addWidget(self.position_label)

        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.sliderMoved.connect(self.on_slider_move)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        progress_layout.addWidget(self.progress_slider)

        self.duration_label = QLabel("0:00")
        progress_layout.addWidget(self.duration_label)
        main_layout.addLayout(progress_layout)
        
        control_layout = QHBoxLayout()

        button_size = QSize(50, 50)
        icon_size = QSize(16, 16)

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

        control_layout.addStretch()
        control_layout.addWidget(self.prev_btn)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.next_btn)
        control_layout.addStretch()

        main_layout.addLayout(control_layout)

        volume_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        self.volume_label = QLabel("50%")
        volume_layout.addWidget(self.volume_label)
        main_layout.addLayout(volume_layout)

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)

    def scan_mp3_files(self):
        self.files_list.clear()
        self.statusBar().showMessage("Сканирую MP3...")

        try:
            files_by_ext = self.scanner.scan_by_extensions(['.mp3'])
            mp3_files = files_by_ext.get('.mp3', [])

            for file_path in mp3_files:
                display_name = os.path.splitext(os.path.basename(file_path))[0]
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, file_path)
                self.files_list.addItem(item)

            self.player.current_playlist = mp3_files
            self.statusBar().showMessage(f"Найдено {len(mp3_files)} MP3 файлов")

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка сканирования: {str(e)}")

    def play_selected_track(self, item):
        if not item:
            return
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            if file_path in self.player.current_playlist:
                self.player.current_index = self.player.current_playlist.index(file_path)

            self.player.play(file_path)
            self.current_track = file_path
            self.load_track_info()
            self.play_btn.setIcon(self.pause_icon)
            self.play_btn.setToolTip("Пауза")
        self.highlight_current_track()

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
            display_name = os.path.splitext(os.path.basename(self.current_track))[0]
            self.track_info.setText(display_name)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMaximized:
                self.switch_to_main_window()
        super().changeEvent(event)

    def switch_to_main_window(self):
        main_window = MainWindow()

        if self.player.current_playlist:
            self._extracted_from_switch_to_main_window_5(main_window)
        main_window.showMaximized()
        self.close()

    def _extracted_from_switch_to_main_window_5(self, main_window):
        main_window.player.current_playlist = self.player.current_playlist
        main_window.player.current_index = self.player.current_index
        main_window.current_track = self.current_track

        main_window.files_list.clear()
        for track_path in self.player.current_playlist:
            display_name = os.path.splitext(os.path.basename(track_path))[0]
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, track_path)
            main_window.files_list.addItem(item)

        if self.player.current_playlist and self.player.current_index >= 0:
            main_window.files_list.setCurrentRow(self.player.current_index)

        main_window.load_track_info()

        if self.player.is_playing():
            main_window.play_btn.setIcon(main_window.pause_icon)
            main_window.play_btn.setToolTip("Пауза")
        else:
            main_window.play_btn.setIcon(main_window.play_icon)
            main_window.play_btn.setToolTip("Воспроизвести")
