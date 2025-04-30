# ╔═════════════════════════════════╗
# ║         📁 Python Project 📁
# ║
# ║  ✨ Team Members ✨
# ║
# ║  🧑‍💻 Elyasaf Cohen 311557227 🧑‍💻
# ║  🧑‍💻 Eldad Cohen   207920711 🧑‍💻
# ║  🧑‍💻 Israel Shlomo 315130344 🧑‍💻
# ║
# ╚══════════════════════════════════╝

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
)
from PySide6.QtGui import QPixmap, QPalette, QBrush, QCursor
from PySide6.QtCore import Qt
from Fronted.Services.api_service import APIService



# ======================================== PORTFOLIO WINDOW ======================================== #
class PortfolioWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌐 Portfolio – Investment Overview 🌐")
        self.resize(950, 650)

        # ===== Set Background Image ===== #
        palette = QPalette()
        background = QPixmap(
            "C:/Users/elyas/PycharmProjects/InvestmentAdvisor/Pictures/background_pic.jpeg")  # ✅ make sure this exists
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        # ===== Title ===== #
        title = QLabel("📊 Your Investment Portfolio 📊")
        title.setStyleSheet("""
            color: white;
            font-size: 22px;
            font-weight: bold;
            padding-bottom: 12px;
        """)

        # ===== Buttons ===== #
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.refresh_button.clicked.connect(self.refresh_portfolio)

        self.save_button = QPushButton("💾 Save to File")
        self.save_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_button.clicked.connect(self.save_portfolio_to_file)

        self.switch_view_button = QPushButton("📈 Table View")
        self.switch_view_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.switch_view_button.clicked.connect(self.toggle_table_view)

        for btn in [self.refresh_button, self.save_button, self.switch_view_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.8);
                    color: #00334e;
                    font-weight: bold;
                    padding: 10px 18px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 255);
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.switch_view_button)
        button_layout.addStretch()

        # ===== Stock List ===== #
        self.stock_list = QListWidget()
        self.stock_list.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.9);
            padding: 12px;
            border-radius: 12px;
            color: #0d47a1;  /* Deep blue text color */
        """)

        self.default_items = [
            "AAPL – 15 shares",
            "MSFT – 10 shares",
            "TSLA – 8 shares",
            "GOOGL – 12 shares",
            "AMZN – 6 shares"
        ]
        for item in self.default_items:
            QListWidgetItem(item, self.stock_list)

        # ===== Stats Table ===== #
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(3)
        self.stats_table.setHorizontalHeaderLabels(["Stock", "Shares", "Value ($)"])
        self.stats_table.setVisible(False)
        self.stats_table.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            color: #0d47a1;  /* Bold blue text */
        """)

        demo_data = [
            ("AAPL", 15, 2700),
            ("MSFT", 10, 3500),
            ("TSLA", 8, 1800),
            ("GOOGL", 12, 3600),
            ("AMZN", 6, 1900)
        ]
        self.stats_table.setRowCount(len(demo_data))
        for row, (stock, shares, value) in enumerate(demo_data):
            self.stats_table.setItem(row, 0, QTableWidgetItem(stock))
            self.stats_table.setItem(row, 1, QTableWidgetItem(str(shares)))
            self.stats_table.setItem(row, 2, QTableWidgetItem(f"{value:,}"))

        # ===== Layout ===== #
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addWidget(self.stock_list)
        layout.addWidget(self.stats_table)
        self.setLayout(layout)

    def refresh_portfolio(self):
        self.stock_list.clear()
        response = APIService.get_portfolio()

        if not response["success"]:
            QMessageBox.critical(self, "Error ❌", response["message"])
            return

        portfolio = response["data"]
        for item in portfolio:
            text = f"{item['stockSymbol']} – {item['amount']} shares"
            QListWidgetItem(text, self.stock_list)
