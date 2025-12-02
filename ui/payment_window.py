from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QRadioButton, QButtonGroup,
                            QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt

class PaymentWindow(QWidget):
    def __init__(self, account_manager):
        super().__init__()
        self.account_manager = account_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Оплата подписки")
        self.setGeometry(300, 300, 400, 300)
        
        layout = QVBoxLayout()
        
        title = QLabel("Выберите тариф подписки")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        tariffs_group = QGroupBox("Доступные тарифы")
        tariffs_layout = QVBoxLayout()
        
        self.tariff_group = QButtonGroup()
        
        monthly_box = QGroupBox()
        monthly_layout = QVBoxLayout()
        self.monthly_radio = QRadioButton("Месячная подписка")
        monthly_price = QLabel("$100 / месяц")
        monthly_features = QLabel("• Полный доступ ко всем функциям\n• Поддержка 4 устройств\n• Автоматическое обновление")
        
        monthly_layout.addWidget(self.monthly_radio)
        monthly_layout.addWidget(monthly_price)
        monthly_layout.addWidget(monthly_features)
        monthly_box.setLayout(monthly_layout)
        
        yearly_box = QGroupBox()
        yearly_layout = QVBoxLayout()
        self.yearly_radio = QRadioButton("Годовая подписка")
        yearly_price = QLabel("$1000 / год (экономия $200)")
        yearly_features = QLabel("• Всё что в месячной подписке\n• 2 месяца бесплатно\n• Приоритетная поддержка")
        
        yearly_layout.addWidget(self.yearly_radio)
        yearly_layout.addWidget(yearly_price)
        yearly_layout.addWidget(yearly_features)
        yearly_box.setLayout(yearly_layout)
        
        self.tariff_group.addButton(self.monthly_radio)
        self.tariff_group.addButton(self.yearly_radio)
        self.monthly_radio.setChecked(True)
        
        tariffs_layout.addWidget(monthly_box)
        tariffs_layout.addWidget(yearly_box)
        tariffs_group.setLayout(tariffs_layout)
        
        button_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Отмена")
        self.pay_btn = QPushButton("Перейти к оплате")
        
        self.cancel_btn.clicked.connect(self.close)
        self.pay_btn.clicked.connect(self.process_payment)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.pay_btn)
        
        layout.addWidget(tariffs_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def process_payment(self):
        plan_type = 'monthly' if self.monthly_radio.isChecked() else 'yearly'
        QMessageBox.information(
            self,
            "Заглушка оплаты",
            f"Выбран тариф: {plan_type}\n\n"
            "В реальном приложении здесь будет:\n"
            "1. Редирект на платежную систему\n"
            "2. Ввод данных карты\n"
            "3. Подтверждение платежа\n\n"
            "Для теста подписка активируется сразу."
        )

        result = self.account_manager.create_payment(plan_type)

        if result and result.get('success'):
            QMessageBox.information(
                self,
                "Успешно!",
                f"Подписка активирована!\n"
                f"Тип: {plan_type}\n"
                f"ID подписки: {result.get('subscription_id')}"
            )
            self.close()
        else:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось создать платеж. Проверьте соединение."
            )