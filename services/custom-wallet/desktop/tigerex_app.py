#!/usr/bin/env python3
"""
TigerEx Desktop App - Windows/Mac/Linux
"""
import sys
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
except:
    print("pip install PyQt6")
    sys.exit(1)

class TigerExApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TigerEx - SERVICE")
        self.setGeometry(100, 100, 400, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        
        # Logo
        layout.addWidget(QLabel("🐯 TigerEx"))
        
        # Login
        layout.addWidget(QLabel("Login / Register"))
        
        # Social buttons
        for provider in ["Google", "Facebook", "Apple"]:
            btn = QPushButton(f"{provider} Login")
            layout.addWidget(btn)
        
        central.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TigerExApp()
    window.show()
    sys.exit(app.exec())
