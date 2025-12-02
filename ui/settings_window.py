from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QComboBox, QCheckBox, QSlider,
                            QGroupBox, QSpinBox, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QSettings

class SettingsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        self.setWindowTitle("Настройки")
        self.setGeometry(300, 300, 500, 600)
        
        layout = QVBoxLayout()
        
        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QVBoxLayout()
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Тема:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Тёмная", "Системная"])
        theme_layout.addWidget(self.theme_combo)
        appearance_layout.addLayout(theme_layout)
        
        # lang_layout = QHBoxLayout()
        # lang_layout.addWidget(QLabel("Язык:"))
        # self.lang_combo = QComboBox()
        # self.lang_combo.addItems(["Русский", "English", "Deutsch"])
        # lang_layout.addWidget(self.lang_combo)
        # appearance_layout.addLayout(lang_layout)
        
        appearance_group.setLayout(appearance_layout)
        
        playback_group = QGroupBox("Воспроизведение")
        playback_layout = QVBoxLayout()
        
        self.crossfade_check = QCheckBox("Кроссфейд между треками")
        self.auto_play_check = QCheckBox("Автовоспроизведение следующего трека")
        self.volume_save_check = QCheckBox("Сохранять уровень громкости")
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Усиление громкости:"))
        self.volume_boost_slider = QSlider(Qt.Horizontal)
        self.volume_boost_slider.setRange(0, 150)
        self.volume_boost_slider.setValue(100)
        volume_layout.addWidget(self.volume_boost_slider)
        volume_layout.addWidget(QLabel("100%"))
        
        playback_layout.addWidget(self.crossfade_check)
        playback_layout.addWidget(self.auto_play_check)
        playback_layout.addWidget(self.volume_save_check)
        playback_layout.addLayout(volume_layout)
        playback_group.setLayout(playback_layout)
        
        library_group = QGroupBox("Библиотека")
        library_layout = QVBoxLayout()
        
        self.auto_scan_check = QCheckBox("Автоматическое сканирование папок")
        self.watch_folder_check = QCheckBox("Отслеживать изменения в папках")
        
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Макс. размер библиотеки (МБ):"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(100, 10000)
        self.limit_spin.setValue(1000)
        limit_layout.addWidget(self.limit_spin)
        
        library_layout.addWidget(self.auto_scan_check)
        library_layout.addWidget(self.watch_folder_check)
        library_layout.addLayout(limit_layout)
        library_group.setLayout(library_layout)
        
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        self.defaults_btn = QPushButton("По умолчанию")
        
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.close)
        self.defaults_btn.clicked.connect(self.load_defaults)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.defaults_btn)
        
        layout.addWidget(appearance_group)
        layout.addWidget(playback_group)
        layout.addWidget(library_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        settings = QSettings("MusicPlayer", "Settings")

        theme_index = settings.value("theme", 1, type=int)
        self.theme_combo.setCurrentIndex(theme_index)

        # lang_index = settings.value("language", 0, type=int)
        # self.lang_combo.setCurrentIndex(lang_index)

        self.crossfade_check.setChecked(settings.value("crossfade", True, type=bool))
        self.auto_play_check.setChecked(settings.value("auto_play", True, type=bool))
        self.volume_save_check.setChecked(settings.value("volume_save", True, type=bool))
        self.volume_boost_slider.setValue(settings.value("volume_boost", 100, type=int))

        self.auto_scan_check.setChecked(settings.value("auto_scan", True, type=bool))
        self.watch_folder_check.setChecked(settings.value("watch_folder", False, type=bool))
        self.limit_spin.setValue(settings.value("library_limit", 1000, type=int))

        self.apply_theme()

    def save_settings(self):
        settings = QSettings("MusicPlayer", "Settings")

        settings.setValue("theme", self.theme_combo.currentIndex())
        # settings.setValue("language", self.lang_combo.currentIndex())

        settings.setValue("crossfade", self.crossfade_check.isChecked())
        settings.setValue("auto_play", self.auto_play_check.isChecked())
        settings.setValue("volume_save", self.volume_save_check.isChecked())
        settings.setValue("volume_boost", self.volume_boost_slider.value())

        settings.setValue("auto_scan", self.auto_scan_check.isChecked())
        settings.setValue("watch_folder", self.watch_folder_check.isChecked())
        settings.setValue("library_limit", self.limit_spin.value())

        self.apply_theme()

        QMessageBox.information(self, "Сохранено", "Настройки сохранены")
        self.close()

    def apply_theme(self):
        theme_index = self.theme_combo.currentIndex()
        app = QApplication.instance()

        if theme_index == 0:  # Голубая тема
            app.setStyleSheet("""
                QWidget {
                    background-color: #e6f2ff;
                    color: #003366;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #66b3ff;
                    border-radius: 8px;
                    margin-top: 1ex;
                    background-color: #cce6ff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 10px 0 10px;
                    color: #0066cc;
                }
                QPushButton {
                    background-color: #80ccff;
                    border: 2px solid #3399ff;
                    border-radius: 6px;
                    padding: 8px 15px;
                    color: #003366;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #66b3ff;
                    border-color: #0066cc;
                }
                QPushButton:pressed {
                    background-color: #3399ff;
                    border-color: #003366;
                }
                QComboBox, QSpinBox, QLineEdit {
                    background-color: #ffffff;
                    border: 2px solid #66b3ff;
                    border-radius: 5px;
                    padding: 5px;
                    color: #003366;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #66b3ff;
                }
                QListWidget {
                    background-color: #ffffff;
                    border: 2px solid #66b3ff;
                    border-radius: 5px;
                    color: #003366;
                }
                QSlider::groove:horizontal {
                    height: 10px;
                    background: #99ccff;
                    border-radius: 5px;
                }
                QSlider::handle:horizontal {
                    background: #0066cc;
                    width: 22px;
                    height: 22px;
                    border-radius: 11px;
                    margin: -6px 0;
                }
                QCheckBox {
                    color: #003366;
                }
                QLabel {
                    color: #003366;
                    font-weight: 500;
                }
                QScrollBar:vertical {
                    background: #cce6ff;
                    width: 12px;
                }
                QScrollBar::handle:vertical {
                    background: #66b3ff;
                    border-radius: 6px;
                    min-height: 20px;
                }
            """)
        elif theme_index == 1:  # Синяя тема
            app.setStyleSheet("""
                QWidget {
                    background-color: #001a33;
                    color: #e6f2ff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #004080;
                    border-radius: 8px;
                    margin-top: 1ex;
                    background-color: #00264d;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 10px 0 10px;
                    color: #80ccff;
                }
                QPushButton {
                    background-color: #004080;
                    border: 2px solid #0059b3;
                    border-radius: 6px;
                    padding: 8px 15px;
                    color: #ffffff;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0059b3;
                    border-color: #0073e6;
                }
                QPushButton:pressed {
                    background-color: #003366;
                    border-color: #004080;
                }
                QComboBox, QSpinBox, QLineEdit {
                    background-color: #00264d;
                    border: 2px solid #004080;
                    border-radius: 5px;
                    padding: 5px;
                    color: #e6f2ff;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #004080;
                }
                QListWidget {
                    background-color: #00264d;
                    border: 2px solid #004080;
                    border-radius: 5px;
                    color: #e6f2ff;
                }
                QSlider::groove:horizontal {
                    height: 10px;
                    background: #003366;
                    border-radius: 5px;
                }
                QSlider::handle:horizontal {
                    background: #0073e6;
                    width: 22px;
                    height: 22px;
                    border-radius: 11px;
                    margin: -6px 0;
                }
                QCheckBox {
                    color: #80ccff;
                }
                QLabel {
                    color: #cce6ff;
                    font-weight: 500;
                }
                QScrollBar:vertical {
                    background: #00264d;
                    width: 12px;
                }
                QScrollBar::handle:vertical {
                    background: #004080;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QMenuBar {
                    background-color: #001a33;
                    color: #e6f2ff;
                }
                QMenuBar::item:selected {
                    background-color: #004080;
                }
                QMenu {
                    background-color: #00264d;
                    border: 1px solid #004080;
                }
                QMenu::item:selected {
                    background-color: #004080;
                }
            """)
    
    def load_defaults(self):
        """Загрузка настроек по умолчанию"""
        self.theme_combo.setCurrentIndex(0)
        self.lang_combo.setCurrentIndex(0)
        self.crossfade_check.setChecked(True)
        self.auto_play_check.setChecked(True)
        self.volume_save_check.setChecked(True)
        self.volume_boost_slider.setValue(100)
        self.auto_scan_check.setChecked(True)
        self.watch_folder_check.setChecked(False)
        self.limit_spin.setValue(1000)