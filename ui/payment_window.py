import os
import json
import webbrowser
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QMessageBox, QTextEdit, QLineEdit,
                            QGroupBox, QFormLayout, QTabWidget, QWidget)
from PyQt5.QtCore import Qt

class PaymentWindow(QDialog):
    def __init__(self, account_manager=None):
        super().__init__()
        self.account_manager = account_manager
        self.client = None
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle("Оплата подписки - Music Player Pro")
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        pay_tab = QWidget()
        pay_layout = QVBoxLayout(pay_tab)
        self.setup_payment_tab(pay_layout)
        tabs.addTab(pay_tab, "💳")

        activate_tab = QWidget()
        activate_layout = QVBoxLayout(activate_tab)
        self.setup_activation_tab(activate_layout)
        tabs.addTab(activate_tab, "🔑")

        layout.addWidget(tabs)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def setup_payment_tab(self, layout):
        title = QLabel("Онлайн оплата через ЮMoney")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #8B00FF;")
        layout.addWidget(title)

        info_group = QGroupBox("Премиум подписка")
        info_layout = QVBoxLayout(info_group)

        self._extracted_from_setup_payment_tab_11(
            "<h2>10 ₽/месяц или 100 ₽/год</h2>", info_layout
        )
        self._extracted_from_setup_payment_tab_11(
            """
        <b>Включено:</b>
        • Сохранение метаданных MP3
        • Поиск текстов песен
        • Авто-распознавание текста
        • Без рекламы
        • Поддержка 4 устройств
        • Приоритетная поддержка
        """,
            info_layout,
        )
        layout.addWidget(info_group)

        tariffs_group = QGroupBox("Выберите тариф")
        tariffs_layout = QVBoxLayout(tariffs_group)

        self._extracted_from_setup_payment_tab_32(
            "Месячная подписка - 10 ₽",
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 6px;
                margin-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """,
            'monthly',
            tariffs_layout,
        )
        self._extracted_from_setup_payment_tab_32(
            "Годовая подписка - 100 ₽",
            """
            QPushButton {
                background-color: #8B00FF;
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #9A32CD;
            }
        """,
            'yearly',
            tariffs_layout,
        )
        layout.addWidget(tariffs_group)

        self._extracted_from_setup_payment_tab_11(
            """
        <b>Как оплатить:</b><br>
        1. Выберите тариф<br>
        2. Оплатите выбранную сумму<br>
        3. Ключ придет на email в течение 5 минут<br>
        4. Активируйте ключ во вкладке "Активация"
        """,
            layout,
        )

    def _extracted_from_setup_payment_tab_32(self, arg0, arg1, arg2, tariffs_layout):
        monthly_btn = QPushButton(arg0)
        monthly_btn.setStyleSheet(arg1)
        monthly_btn.clicked.connect(lambda: self.pay_with_yoomoney(arg2))
        tariffs_layout.addWidget(monthly_btn)

    def _extracted_from_setup_payment_tab_11(self, arg0, arg1):
        price_label = QLabel(arg0)
        price_label.setTextFormat(Qt.RichText)
        arg1.addWidget(price_label)

    def setup_activation_tab(self, layout):
        title = QLabel("Активация лицензионного ключа")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(title)

        form_group = QGroupBox("Введите ключ")
        form_layout = QFormLayout(form_group)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.key_input.setStyleSheet("font-size: 16px; padding: 8px;")
        form_layout.addRow("Лицензионный ключ:", self.key_input)

        layout.addWidget(form_group)

        btn_layout = QHBoxLayout()

        activate_btn = QPushButton("Активировать")
        activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
        """)
        activate_btn.clicked.connect(self.activate_key)
        btn_layout.addWidget(activate_btn)

        layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.status_label.setTextFormat(Qt.RichText)
        layout.addWidget(self.status_label)

        if os.path.exists("license.json"):
            try:
                with open("license.json", "r") as f:
                    license_data = json.load(f)
                    expires = license_data.get('expires', 'неизвестно')
                    status = f"<b>✅ Активная лицензия</b><br>Действует до: {expires}"
                    self.status_label.setText(status)
            except:
                pass

    def pay_with_yoomoney(self, plan_type):
        if not self.account_manager or not self.account_manager.token:
            QMessageBox.warning(self, "Требуется авторизация", "Для оплаты необходимо войти в аккаунт.")
            return

        try:
            if plan_type == 'monthly':
                amount = "10"
                plan_name = "Месячная подписка"
            elif plan_type == 'yearly':
                amount = "100"
                plan_name = "Годовая подписка"
            else:
                amount = "299"
                plan_name = "Подписка"

            from yoomoney import Quickpay

            quickpay = Quickpay(
                receiver="4100119422569693",
                quickpay_form="shop",
                targets=f"Music Player Pro - {plan_name}",
                paymentType="SB",
                sum=amount,
                label=f"{plan_type}_{int(datetime.now().timestamp())}"
            )

            webbrowser.open(quickpay.base_url)

            QMessageBox.information(self, "Оплата",
                f"Открыта страница оплаты ЮMoney.\n"
                f"Тариф: {plan_name}\n"
                f"Сумма: {amount} ₽\n\n"
                "После оплаты ключ придет на email.\n\n"
                f"Номер заказа для связи: {quickpay.label}")

        except Exception as e:
            QMessageBox.warning(self, "Ошибка",
                f"Не удалось создать платеж:\n{str(e)}\n\n"
                "Свяжитесь с поддержкой для получения помощи.")

    def load_settings(self):
        try:
            if os.path.exists("yoomoney_token.txt"):
                with open("yoomoney_token.txt", "r") as f:
                    if token := f.read().strip():
                        from yoomoney import Client
                        self.client = Client(token)
        except:
            pass

    def activate_key(self):
        key = self.key_input.text().strip()

        if not key:
            QMessageBox.warning(self, "Ошибка", "Введите ключ активации")
            return

        if len(key.replace('-', '')) != 16:
            QMessageBox.warning(self, "Ошибка",
                "Неверный формат ключа. Ключ должен содержать 16 символов.")
            return

        if "monthly" in key.lower() or key.startswith("M"):
            plan_type = "monthly"
            expires_days = 30
        elif "yearly" in key.lower() or key.startswith("Y"):
            plan_type = "yearly"
            expires_days = 365
        else:
            plan_type = "yearly"
            expires_days = 90

        license_data = {
            "key": key,
            "activated": datetime.now().strftime("%Y-%m-%d"),
            "expires": (datetime.now() + timedelta(days=expires_days)).strftime("%Y-%m-%d"),
            "product": "music_player_premium",
            "plan_type": plan_type,
            "features": ["metadata", "lyrics", "premium"]
        }

        try:
            with open("license.json", "w") as f:
                json.dump(license_data, f, indent=2)

            self.status_label.setText(
                f"<b>✅ Лицензия активирована!</b><br>"
                f"Тариф: {plan_type}<br>"
                f"Действует до: {license_data['expires']}"
            )

            QMessageBox.information(self, "Успех",
                f"Лицензия успешно активирована!\n"
                f"Тариф: {plan_type.capitalize()}\n"
                "Все премиум-функции разблокированы.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                f"Не удалось сохранить лицензию:\n{str(e)}")

    def check_key(self):
        key = self.key_input.text().strip()

        if not key:
            QMessageBox.warning(self, "Ошибка", "Введите ключ для проверки")
            return

        QMessageBox.information(self, "Проверка",
            f"Ключ: {key}\n\n"
            "Формат ключа корректный.\n"
            "Для активации нажмите 'Активировать'.")
    

