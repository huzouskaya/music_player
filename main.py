import sys
from PyQt5.QtWidgets import QApplication
from ui.mini_player import MiniPlayer

def main():
    app = QApplication(sys.argv)
    window = MiniPlayer()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
