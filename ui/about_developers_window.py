from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class AboutDevelopersWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О разработчиках")
        self.setFixedSize(400, 200)
        self.setWindowModality(Qt.WindowModal)

        layout = QVBoxLayout()

        label = QLabel(
            "Разработчики:\n"
            "• Кабакова Анастасия\n"
            "• Гузовская Александра\n\n"
            "Контакты: kabakova.ap@dvfu.ru, guzovskaya.ac@dvfu.ru"
        )
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)

        layout.addWidget(label)
        layout.addWidget(close_button)
        self.setLayout(layout)