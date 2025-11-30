import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTextEdit, QMessageBox, QFrame, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from auth.payment_verifier import PaymentVerifier

class SubscriptionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Приобрести премиум подписку")
        self.setModal(True)
        self.setFixedSize(500, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_label = QLabel("Премиум подписка")
        header_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Benefits section
        benefits_frame = QFrame()
        benefits_frame.setFrameStyle(QFrame.Box)
        benefits_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border: 2px solid #0078d7;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        benefits_layout = QVBoxLayout(benefits_frame)

        benefits_title = QLabel("Преимущества:")
        benefits_title.setFont(QFont("Arial", 14, QFont.Bold))
        benefits_layout.addWidget(benefits_title)

        benefits_text = QTextEdit()
        benefits_text.setPlainText("""
Поиск текстов песен на Genius
Расширенные функции редактирования
Приоритетная поддержка
Регулярные обновления""")
        benefits_text.setReadOnly(True)
        benefits_text.setMaximumHeight(120)
        benefits_text.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 12px;
            }
        """)
        benefits_layout.addWidget(benefits_text)

        layout.addWidget(benefits_frame)

        # Pricing section
        pricing_label = QLabel("Стоимость: 299₽ / месяц")
        pricing_label.setFont(QFont("Arial", 16, QFont.Bold))
        pricing_label.setAlignment(Qt.AlignCenter)
        pricing_label.setStyleSheet("color: #0078d7;")
        layout.addWidget(pricing_label)

        # Payment methods
        payment_label = QLabel("Способы оплаты:")
        payment_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(payment_label)

        payment_layout = QHBoxLayout()

        payment_methods = [
            ("💳", "Банковская\nкарта"),
            ("📱", "СБП"),
            ("🅿️", "PayPal"),
            ("💰", "Крипто-\nвалюта")
        ]

        for icon, text in payment_methods:
            method_layout = QVBoxLayout()
            method_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            text_label = QLabel(text)
            text_label.setStyleSheet("font-size: 10px; line-height: 1.2;")
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setWordWrap(True)
            
            method_layout.addWidget(icon_label)
            method_layout.addWidget(text_label)
            
            method_widget = QWidget()
            method_widget.setLayout(method_layout)
            method_widget.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 2px;
                }
            """)
            
            payment_layout.addWidget(method_widget)

        payment_widget = QWidget()
        payment_widget.setLayout(payment_layout)

        layout.addWidget(payment_widget)

        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        buttons_layout.addWidget(cancel_btn)

        purchase_btn = QPushButton("Приобрести подписку")
        purchase_btn.clicked.connect(self.purchase_subscription)
        purchase_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                background-color: #0078d7;
                color: white;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        buttons_layout.addWidget(purchase_btn)

        layout.addLayout(buttons_layout)

        footer_label = QLabel("Подписка автоматически продлевается каждый месяц при наличии доступа в интернет.\nВы можете отменить в любое время.")
        footer_label.setStyleSheet("font-size: 10px; color: #666; text-align: center;")
        footer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer_label)

    def purchase_subscription(self):
        reply = QMessageBox.question(self, "Подтверждение оплаты",
                                    "Вы уверены, что хотите приобрести премиум подписку за 299₽?\n\n"
                                    "Оплата будет списана с вашей карты.",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Успех!",
                                    "оздравляем! Премиум подписка активирована!\n\n"
                                    "Теперь вам доступны все функции приложения.")

            verifier = PaymentVerifier()
            verifier.activate_premium()

            self.accept()
