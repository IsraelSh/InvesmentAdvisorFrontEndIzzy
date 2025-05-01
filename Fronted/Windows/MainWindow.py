from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMessageBox,
    QLineEdit, QTextEdit
)
from PySide6.QtGui import QPixmap, QPalette, QBrush, QImage, QCursor
from PySide6.QtCore import Qt, QSize, QRect, QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
import matplotlib.dates as mdates
from urllib.request import urlopen

# Internal Imports
from Fronted.Constants.stock_logos import stock_logos
from Fronted.Services.polygon_service import PolygonService
from Fronted.Services.Ollama_api import ask_ollama
from Fronted.Windows.BuyStocksWindow import BuyStocksWindow
from Fronted.Windows.SellStocksWindow import SellStocksWindow
from Fronted.Windows.OrderHistoryWindow import OrderHistoryWindow
from Fronted.Windows.PortfolioWindow import PortfolioWindow
from Fronted.Windows.AIChatBotWindow import AIChatBotWindow


class MainWindow(QMainWindow):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("📈 Investment Management System 📈")
        self.setMinimumSize(1000, 700)

        # ===== Background Image =====
        self.bg_path = "C:/Users/elyas/PycharmProjects/InvestmentAdvisor/Pictures/background_pic.jpeg"
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()

        palette = QPalette()
        background = QPixmap(self.bg_path)
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        # ===== Layouts =====
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.left_menu = QVBoxLayout()
        self.main_layout.addLayout(self.left_menu, 1)

        # ===== Buttons Menu =====
        self.buttons = [
            ("🟢 Buy Stocks", self.on_buy_stocks_clicked),
            ("🔴 Sell Stocks", self.on_sell_stocks_clicked),
            ("📄 Order History", self.show_order_history_windows),
            ("📁 Portfolio", self.on_portfolio_clicked),
            ("🤖 Ask Chatbot", self.on_askAIChatBot_clicked)
        ]

        for text, slot in self.buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            btn.setCursor(Qt.PointingHandCursor)
            self.left_menu.addWidget(btn)

        # ===== Symbol Input =====
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("e.g., google")
        self.left_menu.addWidget(self.symbol_input)

        self.load_chart_btn = QPushButton("📊 Load Chart")
        self.load_chart_btn.clicked.connect(lambda: self.show_stock_chart(self.symbol_input.text().strip()))
        self.left_menu.addWidget(self.load_chart_btn)

        # ===== Logo Display =====
        self.logo_container = QWidget()
        self.logo_layout = QHBoxLayout(self.logo_container)
        self.logo_layout.setContentsMargins(0, 0, 0, 0)
        self.logo_layout.setAlignment(Qt.AlignCenter)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(120, 120)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid #555;
                border-radius: 12px;
                padding: 2px;
                color: #cccccc;
                font-size: 13px;
            }
        """)
        self.logo_layout.addWidget(self.logo_label)
        self.left_menu.addWidget(self.logo_container, 0, Qt.AlignCenter)

        # ===== AI Chat =====
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask the AI assistant...")
        self.left_menu.addWidget(self.chat_input)

        self.chat_response = QTextEdit()
        self.chat_response.setReadOnly(True)
        self.chat_response.setStyleSheet("""
            background-color: #263238;
            color: #ECEFF1;
            border-radius: 8px;
            padding: 8px;
        """)
        self.chat_response.setMinimumHeight(120)
        self.left_menu.addWidget(self.chat_response)

        self.send_chat_btn = QPushButton("💬 Ask AI assistant")
        self.send_chat_btn.clicked.connect(self.handle_chat_message)
        self.left_menu.addWidget(self.send_chat_btn)

        # ===== Chart Area =====
        self.graph_canvas = FigureCanvas(Figure(figsize=(7, 5)))
        self.main_layout.addWidget(self.graph_canvas, 3)

        # ===== Initial Load =====
        self.show_stock_chart("google")

        # ===== Style =====
        self.setStyleSheet("""
            QPushButton {
                background-color: #2E3B4E;
                color: white;
                font-weight: bold;
                font-size: 15px;
                padding: 10px 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #3C4D63;
            }
            QLineEdit {
                background-color: #ECEFF1;
                color: #263238;
                padding: 8px;
                font-size: 14px;
                border-radius: 6px;
            }
        """)

    def resizeEvent(self, event):
        pixmap = QPixmap(self.bg_path)
        self.bg_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.bg_label.resize(self.size())
        super().resizeEvent(event)

    # ===== Navigation Actions =====
    def on_buy_stocks_clicked(self):
        self.BuyWindow = BuyStocksWindow()
        self.BuyWindow.show()

    def on_sell_stocks_clicked(self):
        self.SellWindow = SellStocksWindow()
        self.SellWindow.show()

    def show_order_history_windows(self):
        self.OrderHistoryWindow = OrderHistoryWindow()
        self.OrderHistoryWindow.show()

    def on_portfolio_clicked(self):
        self.PortfolioWindow = PortfolioWindow()
        self.PortfolioWindow.show()

    def on_askAIChatBot_clicked(self):
        self.AIChatBotWindow = AIChatBotWindow()
        self.AIChatBotWindow.show()

    # ===== Main Feature: Load Stock Chart & Logo =====
    def show_stock_chart(self, symbol="AAPL"):
        mapping = {
            "google": "GOOGL", "apple": "AAPL", "microsoft": "MSFT",
            "amazon": "AMZN", "meta": "META", "facebook": "META",
            "tesla": "TSLA", "intel": "INTC", "nvidia": "NVDA"
        }
        symbol = mapping.get(symbol.lower(), symbol.upper())

        data = PolygonService.get_last_3_months_history(symbol)
        if not data:
            QMessageBox.warning(self, "Error", f"No data found for {symbol}")
            return

        # Draw Chart
        self.graph_canvas.figure.clf()
        fig = self.graph_canvas.figure
        fig.set_facecolor("#1e1e1e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#2b2b2b")

        dates = [datetime.strptime(item["date"], "%Y-%m-%d") for item in data]
        prices = [item["price"] for item in data]

        ax.plot(dates, prices, color="#64b5f6", linewidth=2, marker="o", markersize=5)
        ax.set_title(f"{symbol} – Last 3 Months", fontsize=14, color="#eeeeee")
        ax.set_xlabel("Date", fontsize=11, color="#cccccc")
        ax.set_ylabel("Price ($)", fontsize=11, color="#cccccc")
        ax.tick_params(axis="x", labelrotation=45, colors="#aaaaaa")
        ax.tick_params(axis="y", colors="#aaaaaa")
        ax.set_xticks(dates[::7])
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.3)
        for spine in ax.spines.values():
            spine.set_color("#888888")

        self.graph_canvas.draw()

        # Load Logo
        logo_url = stock_logos.get(symbol)
        self.logo_label.clear()
        if logo_url:
            try:
                image_data = urlopen(logo_url).read()
                image = QImage.fromData(image_data)
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_label.setPixmap(scaled)
            except Exception as e:
                print(f"❌ Failed to load logo: {e}")
                self.logo_label.setText("⚠️ Error loading logo")
        else:
            self.logo_label.setText("🔍 No logo found")

    # ===== Handle Chat Prompt =====
    def handle_chat_message(self):
        prompt = self.chat_input.text().strip()
        if not prompt:
            return

        self.chat_response.setText("🤖 Thinking...")
        self.chat_input.clear()

        def update_response():
            try:
                response = ask_ollama(prompt)
            except Exception as e:
                response = f"❌ Error: {e}"
            self.chat_response.setText(response)

        QTimer.singleShot(100, update_response)
