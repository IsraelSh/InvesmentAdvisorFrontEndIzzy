from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtGui import QPalette, QBrush, QPixmap, QCursor
from PySide6.QtCore import Qt
from Fronted.Services.api_service import APIService  # ודא שיש לך פונקציה create_user שם


class SignUpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📝 Sign Up – Create Your Account")
        self.resize(600, 400)

        # === רקע ===
        palette = QPalette()
        background = QPixmap("C:/Users/elyas/PycharmProjects/InvestmentAdvisor/Pictures/background_pic.jpeg")
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        # === עיצוב כללי ===
        self.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }

            QLineEdit {
                background-color: #e3f2fd;
                color: #0d47a1;
                border: 1px solid #90caf9;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }

            QPushButton {
                background-color: rgba(255, 255, 255, 0.8);
                color: #0d47a1;
                font-weight: bold;
                font-size: 14px;
                border-radius: 10px;
                padding: 10px 20px;
            }

            QPushButton:hover {
                background-color: rgba(255, 255, 255, 1.0);
            }
        """)

        # === שדות קלט ===
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter a username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter a password")
        self.password_input.setEchoMode(QLineEdit.Password)

        # === כפתור רישום ===
        self.signup_button = QPushButton("✅ Create Account")
        self.signup_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.signup_button.clicked.connect(self.handle_signup)

        # === פריסה ===
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        layout.addWidget(QLabel("📝 Sign Up"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)

    def handle_signup(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Missing Fields", "Please fill in all fields.")
            return

        response = APIService.create_user(username, password)
        if response.get("success"):
            QMessageBox.information(self, "Success", response["message"])
            self.close()
        else:
            QMessageBox.critical(self, "Error", response["message"])
