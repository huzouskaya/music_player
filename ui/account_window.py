from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QMessageBox, QGroupBox, QLineEdit, QTabWidget, QFormLayout)
from PyQt5.QtCore import Qt
import json

class AccountWindow(QWidget):
    def __init__(self, account_manager):
        super().__init__()
        self.account_manager = account_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Мой аккаунт")
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()

        if not self.account_manager.token:
            self.show_login_form(layout)
            self.setLayout(layout)
            return

        self.user_group = QGroupBox("Информация о пользователе")
        user_layout = QVBoxLayout()

        self.email_label = QLabel("Email: ")
        self.created_label = QLabel("Дата регистрации: ")
        self.last_login_label = QLabel("Последний вход: ")

        user_layout.addWidget(self.email_label)
        user_layout.addWidget(self.created_label)
        user_layout.addWidget(self.last_login_label)
        self.user_group.setLayout(user_layout)

        self.subscription_group = QGroupBox("Подписка")
        subscription_layout = QVBoxLayout()

        self.plan_label = QLabel("Тариф: Нет активной подписки")
        self.end_date_label = QLabel("Действует до: ")
        self.days_left_label = QLabel("Осталось дней: ")

        subscription_layout.addWidget(self.plan_label)
        subscription_layout.addWidget(self.end_date_label)
        subscription_layout.addWidget(self.days_left_label)
        self.subscription_group.setLayout(subscription_layout)

        self.devices_group = QGroupBox("Устройства (макс. 4)")
        devices_layout = QVBoxLayout()

        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(3)
        self.devices_table.setHorizontalHeaderLabels(["Хеш устройства", "Имя", "Последняя активность"])
        self.devices_table.horizontalHeader().setStretchLastSection(True)

        devices_layout.addWidget(self.devices_table)
        self.devices_group.setLayout(devices_layout)

        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить")
        self.remove_device_btn = QPushButton("Удалить выбранное устройство")
        self.buy_subscription_btn = QPushButton("Купить подписку")
        self.logout_btn = QPushButton("Выйти")

        self.refresh_btn.clicked.connect(self.load_account_info)
        self.remove_device_btn.clicked.connect(self.remove_selected_device)
        self.buy_subscription_btn.clicked.connect(self.open_payment)
        self.logout_btn.clicked.connect(self.logout)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.remove_device_btn)
        button_layout.addWidget(self.buy_subscription_btn)
        button_layout.addWidget(self.logout_btn)

        layout.addWidget(self.user_group)
        layout.addWidget(self.subscription_group)
        layout.addWidget(self.devices_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_account_info(self):
        info = self.account_manager.get_account_info()

        if info and info.get('success'):
            user = info['user']
            subscription = info.get('subscription')
            devices = info.get('devices', [])

            self.email_label.setText(f"Email: {user['email']}")
            self.created_label.setText(f"Дата регистрации: {user['created_at'][:10]}")
            self.last_login_label.setText(f"Последний вход: {user['last_login'][:19] if user['last_login'] else 'Никогда'}")

            if subscription:
                self._extracted_from_load_account_info_16(subscription)
            else:
                self.plan_label.setText("Тариф: Нет активной подписки")
                self.end_date_label.setText("Действует до: -")
                self.days_left_label.setText("Осталось дней: -")

            self.devices_table.setRowCount(len(devices))
            for row, device in enumerate(devices):
                self.devices_table.setItem(row, 0, QTableWidgetItem(device['device_hash'][:16] + '...'))
                self.devices_table.setItem(row, 1, QTableWidgetItem(device['device_name'] or 'Без имени'))
                self.devices_table.setItem(row, 2, QTableWidgetItem(device['last_active'][:19]))

    def _extracted_from_load_account_info_16(self, subscription):
        self.plan_label.setText(f"Тариф: {subscription['plan_type']} (${subscription['price']})")
        self.end_date_label.setText(f"Действует до: {subscription['end_date'][:10]}")

        from datetime import datetime
        end_date = datetime.fromisoformat(subscription['end_date'].replace('Z', '+00:00'))
        days_left = (end_date - datetime.now()).days
        self.days_left_label.setText(f"Осталось дней: {days_left}")

    def remove_selected_device(self):
        selected = self.devices_table.currentRow()
        if selected >= 0:
            device_hash = self.devices_table.item(selected, 0).text().split('...')[0]

            reply = QMessageBox.question(
                self, 'Подтверждение',
                'Вы уверены, что хотите удалить это устройство?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                if self.account_manager.remove_device(device_hash):
                    QMessageBox.information(self, "Успех", "Устройство удалено")
                    self.load_account_info()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить устройство")

    def open_payment(self):
        from .payment_window import PaymentWindow
        self.payment_window = PaymentWindow(self.account_manager)
        self.payment_window.show()

    def show_login_form(self, layout):
        tabs = QTabWidget()

        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)

        login_form = QFormLayout()
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("email@example.com")
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Пароль")

        login_form.addRow("Email:", self.login_email)
        login_form.addRow("Пароль:", self.login_password)

        login_layout.addLayout(login_form)

        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.login)
        login_layout.addWidget(login_btn)

        tabs.addTab(login_tab, "Вход")

        register_tab = QWidget()
        register_layout = QVBoxLayout(register_tab)

        register_form = QFormLayout()
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("email@example.com")
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setPlaceholderText("Пароль")
        self.register_confirm = QLineEdit()
        self.register_confirm.setEchoMode(QLineEdit.Password)
        self.register_confirm.setPlaceholderText("Подтвердите пароль")

        register_form.addRow("Email:", self.register_email)
        register_form.addRow("Пароль:", self.register_password)
        register_form.addRow("Подтверждение:", self.register_confirm)

        register_layout.addLayout(register_form)

        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.register)
        register_layout.addWidget(register_btn)

        tabs.addTab(register_tab, "Регистрация")

        layout.addWidget(tabs)

    def rebuild_ui(self):
        if layout := self.layout():
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            layout.deleteLater()

        new_layout = QVBoxLayout()

        if not self.account_manager.token:
            self.show_login_form(new_layout)
            self.setLayout(new_layout)
            return

        self.user_group = QGroupBox("Информация о пользователе")
        user_layout = QVBoxLayout()

        self.email_label = QLabel("Email: ")
        self.created_label = QLabel("Дата регистрации: ")
        self.last_login_label = QLabel("Последний вход: ")

        user_layout.addWidget(self.email_label)
        user_layout.addWidget(self.created_label)
        user_layout.addWidget(self.last_login_label)
        self.user_group.setLayout(user_layout)

        self.subscription_group = QGroupBox("Подписка")
        subscription_layout = QVBoxLayout()

        self.plan_label = QLabel("Тариф: Нет активной подписки")
        self.end_date_label = QLabel("Действует до: ")
        self.days_left_label = QLabel("Осталось дней: ")

        subscription_layout.addWidget(self.plan_label)
        subscription_layout.addWidget(self.end_date_label)
        subscription_layout.addWidget(self.days_left_label)
        self.subscription_group.setLayout(subscription_layout)

        self.devices_group = QGroupBox("Устройства (макс. 4)")
        devices_layout = QVBoxLayout()

        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(3)
        self.devices_table.setHorizontalHeaderLabels(["Хеш устройства", "Имя", "Последняя активность"])
        self.devices_table.horizontalHeader().setStretchLastSection(True)

        devices_layout.addWidget(self.devices_table)
        self.devices_group.setLayout(devices_layout)

        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить")
        self.remove_device_btn = QPushButton("Удалить выбранное устройство")
        self.buy_subscription_btn = QPushButton("Купить подписку")
        self.logout_btn = QPushButton("Выйти")

        self.refresh_btn.clicked.connect(self.load_account_info)
        self.remove_device_btn.clicked.connect(self.remove_selected_device)
        self.buy_subscription_btn.clicked.connect(self.open_payment)
        self.logout_btn.clicked.connect(self.logout)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.remove_device_btn)
        button_layout.addWidget(self.buy_subscription_btn)
        button_layout.addWidget(self.logout_btn)

        new_layout.addWidget(self.user_group)
        new_layout.addWidget(self.subscription_group)
        new_layout.addWidget(self.devices_group)
        new_layout.addLayout(button_layout)

        self.setLayout(new_layout)
        self.load_account_info()

    def login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if self.account_manager.login(email, password):
            # QMessageBox.information(self, "Успех", "Вход выполнен успешно!")
            self.rebuild_ui()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный email или пароль")

    def register(self):
        email = self.register_email.text().strip()
        password = self.register_password.text().strip()
        confirm = self.register_confirm.text().strip()

        if not email or not password or not confirm:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть не менее 6 символов")
            return

        if self.account_manager.register(email, password):
            # QMessageBox.information(self, "Успех", "Регистрация выполнена успешно! Теперь войдите в аккаунт.")
            self.login_email.setText(email)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось зарегистрироваться. Возможно, email уже используется.")

    def logout(self):
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите выйти из аккаунта?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.account_manager.logout()
            # QMessageBox.information(self, "Успех", "Вы вышли из аккаунта")
            self.rebuild_ui()
