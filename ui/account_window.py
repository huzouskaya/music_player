from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt
import json

class AccountWindow(QWidget):
    def __init__(self, account_manager):
        super().__init__()
        self.account_manager = account_manager
        self.init_ui()
        self.load_account_info()
    
    def init_ui(self):
        self.setWindowTitle("Мой аккаунт")
        self.setGeometry(300, 300, 600, 400)
        
        layout = QVBoxLayout()
        
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
        
        self.refresh_btn.clicked.connect(self.load_account_info)
        self.remove_device_btn.clicked.connect(self.remove_selected_device)
        self.buy_subscription_btn.clicked.connect(self.open_payment)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.remove_device_btn)
        button_layout.addWidget(self.buy_subscription_btn)
        
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

    # TODO Rename this here and in `load_account_info`
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