from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class AboutAppWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О приложении")
        self.setFixedSize(400, 200)
        self.setWindowModality(Qt.WindowModal)

        layout = QVBoxLayout()

        label = QLabel(
            "Версия: 1.0.0\n"
            "Платформа: Настольное приложение\n"
            "Назначение: Прослушивание аудиофайлов\n"
        )
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)

        layout.addWidget(label)
        layout.addWidget(close_button)
        self.setLayout(layout)