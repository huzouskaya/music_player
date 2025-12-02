# themes.py
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings

class ThemeManager:
    
    @staticmethod
    def get_theme_stylesheet(theme_index):
        if theme_index == 0:
            return """
                QWidget {
                    background-color: #e6f2ff;
                    color: #003366;
                }
                QMainWindow {
                    background-color: #e6f2ff;
                }
                QPushButton {
                    background-color: #80ccff;
                    border: 2px solid #3399ff;
                    border-radius: 5px;
                    padding: 5px;
                    color: #003366;
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
                    border-radius: 3px;
                    padding: 5px;
                    color: #003366;
                }
                QListWidget {
                    background-color: #ffffff;
                    border: 2px solid #66b3ff;
                    border-radius: 5px;
                    color: #003366;
                }
                QSlider::groove:horizontal {
                    height: 8px;
                    background: #99ccff;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #0066cc;
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                    margin: -5px 0;
                }
                QLabel {
                    color: #003366;
                }
                QStatusBar {
                    background-color: #cce6ff;
                    color: #003366;
                }
            """
        elif theme_index == 1:
            return """
                QWidget {
                    background-color: #001a33;
                    color: #e6f2ff;
                }
                QMainWindow {
                    background-color: #001a33;
                }
                QPushButton {
                    background-color: #004080;
                    border: 2px solid #0059b3;
                    border-radius: 5px;
                    padding: 5px;
                    color: #ffffff;
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
                    border-radius: 3px;
                    padding: 5px;
                    color: #e6f2ff;
                }
                QListWidget {
                    background-color: #00264d;
                    border: 2px solid #004080;
                    border-radius: 5px;
                    color: #e6f2ff;
                }
                QSlider::groove:horizontal {
                    height: 8px;
                    background: #003366;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #0073e6;
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                    margin: -5px 0;
                }
                QLabel {
                    color: #cce6ff;
                }
                QStatusBar {
                    background-color: #00264d;
                    color: #e6f2ff;
                }
            """
        return ""
    
    @staticmethod
    def apply_theme(theme_index):
        stylesheet = ThemeManager.get_theme_stylesheet(theme_index)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
    
    @staticmethod
    def load_theme_from_settings():
        settings = QSettings("MusicPlayer", "Settings")
        theme_index = settings.value("theme", 0, type=int)
        ThemeManager.apply_theme(theme_index)
        return theme_index