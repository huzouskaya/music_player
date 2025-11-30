import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from auth.payment_verifier import PaymentVerifier

def main():
    # verifier = PaymentVerifier()
    # if not verifier.verify_license():
    #     print("Лицензия не действительна. Пожалуйста, приобретите подписку.")
    #     return
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()