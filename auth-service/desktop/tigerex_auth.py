#!/usr/bin/env python3
"""
TigerEx Authentication Desktop App (Windows/Mac/Linux)
Built with PyQt6 - Works on all desktop platforms
"""
import sys
import random
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class TigerExAuth(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TigerEx - Authentication")
        self.setFixedSize(450, 700)
        self.setStyleSheet("background-color: #1f2937;")
        
        self.current_view = "login"
        self.user_logged_in = None
        
        # Countries (200+)
        self.countries = [
            ("+1", "🇺🇸 US"), ("+1", "🇨🇦 CA"), ("+44", "🇬🇧 UK"), ("+91", "🇮🇳 IN"),
            ("+86", "🇨🇳 CN"), ("+81", "🇯🇵 JP"), ("+49", "🇩🇪 DE"), ("+33", "🇫🇷 FR"),
            ("+55", "🇧🇷 BR"), ("+7", "🇷🇺 RU"), ("+20", "🇪🇬 EG"), ("+966", "🇸🇦 SA"),
            ("+971", "🇦🇪 AE"), ("+92", "🇵🇰 PK"), ("+880", "🇧🇩 BD"), ("+65", "🇸🇬 SG"),
            ("+60", "🇲🇾 MY"), ("+62", "🇮🇩 ID"), ("+84", "🇻🇳 VN"), ("+63", "🇵🇭 PH"),
        ]
        
        self.init_ui()
    
    def init_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Logo
        logo = QLabel("🐯 TigerEx")
        logo.setStyleSheet("font-size: 36px; font-weight: bold; color: #fbbf24;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        layout.addStretch()
        self.setCentralWidget(widget)
        self.show_login()
    
    # ==================== LOGIN ====================
    def show_login(self):
        self.clear_layout()
        layout = self.centralWidget().layout()
        
        title = QLabel("Welcome Back")
        title.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.insertWidget(0, title)
        
        # Social Login
        social_box = QHBoxLayout()
        social_box.setSpacing(10)
        for provider in [("Google", "🔴"), ("Facebook", "🔵"), ("Twitter", "⚫"), ("Apple", "🍎")]:
            btn = QPushButton(provider[1])
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("QPushButton { border-radius: 25px; background: #374151; color: white; } QPushButton:hover { background: #4b5563; }")
            btn.clicked.connect(lambda _, p=provider[0]: self.social_login(p))
            social_box.addWidget(btn)
        
        social_widget = QWidget()
        social_widget.setLayout(social_box)
        layout.addWidget(social_widget)
        
        # Or divider
        or_label = QLabel("or")
        or_label.setStyleSheet("color: #9ca3af;")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(or_label)
        
        # Email/Phone
        self.et_email = QLineEdit()
        self.et_email.setPlaceholderText("Email or Phone")
        self.et_email.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        layout.addWidget(self.et_email)
        
        # Password
        self.et_password = QLineEdit()
        self.et_password.setPlaceholderText("Password")
        self.et_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.et_password.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        layout.addWidget(self.et_password)
        
        # Show password toggle
        self.cb_show_pass = QCheckBox("Show password")
        self.cb_show_pass.setStyleSheet("color: #9ca3af;")
        self.cb_show_pass.toggled.connect(self.toggle_password)
        layout.addWidget(self.cb_show_pass)
        
        # Stay logged
        self.cb_stay = QCheckBox("Stay logged in (30 days)")
        self.cb_stay.setStyleSheet("color: #9ca3af;")
        layout.addWidget(self.cb_stay)
        
        # Forgot password
        btn_forgot = QPushButton("Forgot Password?")
        btn_forgot.setStyleSheet("QPushButton { background: transparent; color: #fbbf24; border: none; }")
        btn_forgot.clicked.connect(self.show_forgot)
        layout.addWidget(btn_forgot)
        
        # Login button
        btn_login = QPushButton("Login")
        btn_login.setStyleSheet("QPushButton { background: #fbbf24; color: #1f2937; border-radius: 10px; padding: 14px; font-weight: bold; font-size: 16px; } QPushButton:hover { background: #f59e0b; }")
        btn_login.clicked.connect(self.handle_login)
        layout.addWidget(btn_login)
        
        # Switch
        btn_switch = QPushButton("Don't have an account? Sign Up")
        btn_switch.setStyleSheet("QPushButton { background: transparent; color: #9ca3af; border: none; }")
        btn_switch.clicked.connect(self.show_register)
        layout.addWidget(btn_switch)
    
    def toggle_password(self):
        if self.cb_show_pass.isChecked():
            self.et_password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.et_password.setEchoMode(QLineEdit.EchoMode.Password)
    
    # ==================== REGISTER ====================
    def show_register(self):
        self.clear_layout()
        layout = self.centralWidget().layout()
        
        title = QLabel("Create Account")
        title.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.insertWidget(0, title)
        
        # Email
        self.et_email = QLineEdit()
        self.et_email.setPlaceholderText("Email")
        self.et_email.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        layout.addWidget(self.et_email)
        
        # Phone with country
        phone_layout = QHBoxLayout()
        self.cb_country = QComboBox()
        for code, name in self.countries:
            self.cb_country.addItem(name, code)
        self.cb_country.setStyleSheet("QComboBox { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        self.cb_country.setFixedWidth(100)
        
        self.et_phone = QLineEdit()
        self.et_phone.setPlaceholderText("Phone")
        self.et_phone.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        
        phone_layout.addWidget(self.cb_country)
        phone_layout.addWidget(self.et_phone)
        layout.addLayout(phone_layout)
        
        # Password
        self.et_password = QLineEdit()
        self.et_password.setPlaceholderText("Password")
        self.et_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.et_password.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        layout.addWidget(self.et_password)
        
        # Confirm
        self.et_confirm = QLineEdit()
        self.et_confirm.setPlaceholderText("Confirm Password")
        self.et_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.et_confirm.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        layout.addWidget(self.et_confirm)
        
        # Terms
        self.cb_terms = QCheckBox("I agree to TigerEx Terms & Conditions")
        self.cb_terms.setStyleSheet("color: #9ca3af;")
        layout.addWidget(self.cb_terms)
        
        # Register button
        btn = QPushButton("Continue")
        btn.setStyleSheet("QPushButton { background: #fbbf24; color: #1f2937; border-radius: 10px; padding: 14px; font-weight: bold; font-size: 16px; }")
        btn.clicked.connect(self.handle_register)
        layout.addWidget(btn)
        
        # Switch
        btn_switch = QPushButton("Already have an account? Login")
        btn_switch.setStyleSheet("QPushButton { background: transparent; color: #9ca3af; border: none; }")
        btn_switch.clicked.connect(self.show_login)
        layout.addWidget(btn_switch)
    
    # ==================== FORGOT PASSWORD ====================
    def show_forgot(self):
        self.clear_layout()
        layout = self.centralWidget().layout()
        
        btn_back = QPushButton("← Back")
        btn_back.setStyleSheet("QPushButton { background: transparent; color: #9ca3af; border: none; }")
        btn_back.clicked.connect(self.show_login)
        layout.addWidget(btn_back)
        
        title = QLabel("Reset Password")
        title.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.et_email = QLineEdit()
        self.et_email.setPlaceholderText("Email or Phone")
        self.et_email.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        layout.addWidget(self.et_email)
        
        btn = QPushButton("Continue")
        btn.setStyleSheet("QPushButton { background: #fbbf24; color: #1f2937; border-radius: 10px; padding: 14px; font-weight: bold; }")
        btn.clicked.connect(self.handle_forgot)
        layout.addWidget(btn)
    
    # ==================== BIND EMAIL/PHONE ====================
    def show_bind(self):
        self.clear_layout()
        layout = self.centralWidget().layout()
        
        title = QLabel("Complete Your Profile")
        title.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        label = QLabel("Bind your email and phone")
        label.setStyleSheet("color: #9ca3af;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self.et_email = QLineEdit()
        self.et_email.setPlaceholderText("Email")
        self.et_email.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        layout.addWidget(self.et_email)
        
        btn = QPushButton("Send Email Code")
        btn.setStyleSheet("QPushButton { background: #fbbf24; color: #1f2937; border-radius: 8px; padding: 10px; }")
        btn.clicked.connect(lambda: self.show_message("Code sent!"))
        layout.addWidget(btn)
        
        self.et_code = QLineEdit()
        self.et_code.setPlaceholderText("Verification code")
        self.et_code.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        layout.addWidget(self.et_code)
        
        self.et_phone = QLineEdit()
        self.et_phone.setPlaceholderText("Phone")
        self.et_phone.setStyleSheet("QLineEdit { background: #374151; border: 1px solid #4b5563; border-radius: 8px; padding: 12px; color: white; }")
        layout.addWidget(self.et_phone)
        
        btn2 = QPushButton("Send Phone Code")
        btn2.setStyleSheet("QPushButton { background: #fbbf24; color: #1f2937; border-radius: 8px; padding: 10px; }")
        layout.addWidget(btn2)
        
        btn3 = QPushButton("Continue to Dashboard")
        btn3.setStyleSheet("QPushButton { background: #fbbf24; color: #1f2937; border-radius: 10px; padding: 14px; font-weight: bold; }")
        btn3.clicked.connect(self.show_dashboard)
        layout.addWidget(btn3)
    
    # ==================== DASHBOARD ====================
    def show_dashboard(self):
        self.clear_layout()
        layout = self.centralWidget().layout()
        
        icon = QLabel("👤")
        icon.setStyleSheet("font-size: 60px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        
        title = QLabel("My Account")
        title.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Info rows
        for icon_text, title_text, value in [
            ("📧", "Email", "user@example.com"),
            ("📱", "Phone", "+1234567890"),
            ("🛡️", "2FA", "Disabled"),
            ("🪪", "KYC", "Not Verified"),
        ]:
            row = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            icon_label = QLabel(icon_text)
            icon_label.setStyleSheet("font-size: 20px;")
            
            title_label = QLabel(title_text)
            title_label.setStyleSheet("color: #9ca3af;")
            
            value_label = QLabel(value)
            value_label.setStyleSheet("color: white;")
            
            row_layout.addWidget(icon_label)
            row_layout.addWidget(title_label)
            row_layout.addStretch()
            row_layout.addWidget(value_label)
            
            row.setLayout(row_layout)
            row.setStyleSheet("background: #374151; border-radius: 10px; padding: 15px;")
            layout.addWidget(row)
        
        # Logout
        btn = QPushButton("Logout")
        btn.setStyleSheet("QPushButton { background: #dc2626; color: white; border-radius: 10px; padding: 14px; }")
        btn.clicked.connect(self.show_login)
        layout.addWidget(btn)
    
    # ==================== HANDLERS ====================
    def handle_login(self):
        identifier = self.et_email.text().strip()
        password = self.et_password.text()
        
        if not identifier or not password:
            self.show_message("Please fill all fields")
            return
        
        # Check user exists
        if not self.check_user_exists(identifier):
            self.show_message("User not found. Please register.")
            self.show_register()
            return
        
        if self.is_2fa_enabled(identifier):
            self.show_message("Enter 2FA code")
            return
        
        self.show_message("Login successful!")
        self.show_dashboard()
    
    def handle_register(self):
        email = self.et_email.text().strip()
        phone = self.et_phone.text().strip()
        password = self.et_password.text()
        confirm = self.et_confirm.text()
        
        if not email or not phone or not password:
            self.show_message("Please fill all fields")
            return
        
        if password != confirm:
            self.show_message("Passwords do not match")
            return
        
        if self.check_user_exists(email):
            self.show_message("User already exists. Login.")
            self.show_login()
            return
        
        if not self.cb_terms.isChecked():
            self.show_message("Accept terms and conditions")
            return
        
        # Send verification codes
        self.show_message("Verification codes sent!")
        # Would show verification input
    
    def handle_forgot(self):
        identifier = self.et_email.text().strip()
        
        if not identifier:
            self.show_message("Enter email or phone")
            return
        
        if not self.check_user_exists(identifier):
            self.show_message("User not found. Register.")
            self.show_register()
            return
        
        self.show_message("Reset code sent!")
    
    def social_login(self, provider):
        self.show_message(f"Login with {provider}...")
        # In production: use OAuth
        self.show_bind()
    
    # ==================== HELPERS ====================
    def clear_layout(self):
        layout = self.centralWidget().layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear nested layout
                while item.layout().count():
                    nested = item.layout().takeAt(0)
                    nested.widget().deleteLater()
    
    def check_user_exists(self, identifier):
        # Call backend API
        return False
    
    def is_2fa_enabled(self, identifier):
        # Call backend API
        return False
    
    def show_message(self, message):
        msg = QMessageBox(self)
        msg.setText(message)
        msg.setStyleSheet("QMessageBox { background: #1f2937; color: white; }")
        msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TigerExAuth()
    window.show()
    sys.exit(app.exec())