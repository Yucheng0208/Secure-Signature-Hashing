import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QLabel, QFileDialog, QPushButton, QVBoxLayout, QWidget, QTextEdit, 
    QMessageBox, QMenuBar, QAction
)
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint


class SignatureDecoder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signature Decoder")
        self.setGeometry(200, 200, 1000, 700)

        # 設定選單列
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu("File")
        edit_menu = self.menu_bar.addMenu("Edit")
        help_menu = self.menu_bar.addMenu("Help")

        # File 選單
        open_action = QAction("Open JSON", self)
        open_action.triggered.connect(self.load_signature)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit 選單
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear_canvas)
        edit_menu.addAction(clear_action)

        # Help 選單
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # 介面組件
        self.load_button = QPushButton("Load JSON Signature File", self)
        self.load_button.clicked.connect(self.load_signature)

        # 訊息與座標顯示
        self.message_display = QTextEdit(self)
        self.message_display.setReadOnly(True)
        self.message_display.setPlaceholderText("Original Message will be displayed here...")

        self.coordinates_display = QTextEdit(self)
        self.coordinates_display.setReadOnly(True)
        self.coordinates_display.setPlaceholderText("Signature Coordinates will be displayed here...")

        # 畫布
        self.canvas_label = QLabel(self)
        self.canvas = QPixmap(950, 500)
        self.canvas.fill(Qt.white)
        self.canvas_label.setPixmap(self.canvas)
        self.signature_points = []  # 存儲簽名座標，防止視窗調整時消失

        # 佈局
        layout = QVBoxLayout()
        layout.setMenuBar(self.menu_bar)
        layout.addWidget(self.load_button)
        layout.addWidget(QLabel("Original Message:"))
        layout.addWidget(self.message_display)
        layout.addWidget(QLabel("Signature Coordinates:"))
        layout.addWidget(self.coordinates_display)
        layout.addWidget(QLabel("Restored Signature (Adjusted to Fit Screen):"))
        layout.addWidget(self.canvas_label, 1)
        self.setLayout(layout)

    def load_signature(self):
        """讀取 JSON 簽名檔案並繪製簽名"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if not file_path:
            return

        valid_signature = self.load_json(file_path)

        if valid_signature:
            QMessageBox.information(self, "Verification", "Signature verification successful!", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Verification Failed", "The file does not contain a valid signature.", QMessageBox.Ok)

    def load_json(self, file_path):
        """處理 JSON 檔案"""
        with open(file_path, "r") as file:
            data = json.load(file)

        if "Signature" not in data or "Message" not in data:
            return False

        self.signature_points = data["Signature"]  # 存儲座標
        self.display_signature()
        self.message_display.setText(data["Message"])
        self.coordinates_display.setText(json.dumps(data["Signature"], indent=4))
        return True

    def display_signature(self):
        """繪製還原的簽名"""
        self.canvas.fill(Qt.white)
        painter = QPainter(self.canvas)
        painter.setPen(QPen(Qt.blue, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        prev_point = None
        for point in self.signature_points:
            current_point = QPoint(point["X"], point["Y"])
            if prev_point is not None:
                painter.drawLine(prev_point, current_point)
            prev_point = current_point

        painter.end()
        self.canvas_label.setPixmap(self.canvas)

    def clear_canvas(self):
        """清空畫布與顯示內容"""
        self.canvas.fill(Qt.white)
        self.canvas_label.setPixmap(self.canvas)
        self.message_display.clear()
        self.coordinates_display.clear()
        self.signature_points = []  # 清空座標

    def show_about(self):
        """顯示關於資訊"""
        QMessageBox.information(self, "About", "This is a JSON-only signature verification and restoration tool.")

    def resizeEvent(self, event):
        """當視窗大小改變時，自適應畫布大小並重新繪製簽名"""
        new_width = self.width() - 50
        new_height = int(self.height() / 2)

        self.canvas = QPixmap(new_width, new_height)
        self.canvas.fill(Qt.white)
        self.canvas_label.setPixmap(self.canvas)

        if self.signature_points:  # 重新繪製簽名
            self.display_signature()

        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignatureDecoder()
    window.show()
    sys.exit(app.exec_())
