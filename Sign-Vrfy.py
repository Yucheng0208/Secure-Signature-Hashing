import sys
import json
import csv
import re
from PyQt5.QtWidgets import (
    QApplication, QLabel, QFileDialog, QPushButton, QVBoxLayout, QWidget, QTextEdit, 
    QMessageBox, QMenuBar, QAction, QSplitter
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
        open_action = QAction("Open", self)
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
        self.load_button = QPushButton("Load Signature File", self)
        self.load_button.clicked.connect(self.load_signature)

        # 讓訊息與座標使用左右分割
        self.message_display = QTextEdit(self)
        self.message_display.setReadOnly(True)
        self.message_display.setPlaceholderText("Original Message will be displayed here...")

        self.coordinates_display = QTextEdit(self)
        self.coordinates_display.setReadOnly(True)
        self.coordinates_display.setPlaceholderText("Signature Coordinates will be displayed here...")

        # 分割區塊（讓訊息與座標水平排列）
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.message_display)
        self.splitter.addWidget(self.coordinates_display)
        self.splitter.setSizes([400, 400])

        # 調整畫布，使其佔據足夠大的空間
        self.canvas_label = QLabel(self)
        self.canvas = QPixmap(950, 500)  # 預設較大尺寸
        self.canvas.fill(Qt.white)
        self.canvas_label.setPixmap(self.canvas)

        # 佈局
        layout = QVBoxLayout()
        layout.setMenuBar(self.menu_bar)
        layout.addWidget(self.load_button)
        layout.addWidget(QLabel("Original Message & Signature Coordinates:"))
        layout.addWidget(self.splitter)
        layout.addWidget(QLabel("Restored Signature (Adjusted to Fit Screen):"))
        layout.addWidget(self.canvas_label, 1)
        self.setLayout(layout)

    def load_signature(self):
        """讀取簽名 JSON / CSV / TXT 檔案並繪製簽名"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Signature File", "", "Supported Files (*.json *.csv *.txt)")
        if not file_path:
            return

        file_extension = file_path.split(".")[-1].lower()
        valid_signature = False

        if file_extension == "json":
            valid_signature = self.load_json(file_path)
        elif file_extension == "csv":
            valid_signature = self.load_csv(file_path)
        elif file_extension == "txt":
            valid_signature = self.load_txt(file_path)

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

        self.display_signature(data["Signature"])
        self.message_display.setText(data["Message"])
        self.coordinates_display.setText(json.dumps(data["Signature"], indent=4))
        return True

    def load_csv(self, file_path):
        """處理 CSV 檔案"""
        signature_points = []
        message = ""
        with open(file_path, "r") as file:
            reader = csv.reader(file)
            next(reader)  # 跳過標題行
            for row in reader:
                if row[0] == "Message":
                    message = row[1]
                elif row[0] == "X":
                    continue
                else:
                    try:
                        x = int(row[0])
                        y = int(row[1])
                        signature_points.append({"X": x, "Y": y})
                    except ValueError:
                        pass  # 避免錯誤資料

        if not signature_points:
            return False

        self.display_signature(signature_points)
        self.message_display.setText(message)
        self.coordinates_display.setText(json.dumps(signature_points, indent=4))
        return True

    def load_txt(self, file_path):
        """處理 TXT 檔案"""
        signature_points = []
        message = ""
        with open(file_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith("Message:"):
                message = line.replace("Message:", "").strip()
            elif re.match(r"^\d+,\d+$", line.strip()):
                x, y = map(int, line.strip().split(","))
                signature_points.append({"X": x, "Y": y})

        if not signature_points:
            return False

        self.display_signature(signature_points)
        self.message_display.setText(message)
        self.coordinates_display.setText(json.dumps(signature_points, indent=4))
        return True

    def display_signature(self, signature_points):
        """繪製還原的簽名"""
        self.canvas.fill(Qt.white)
        painter = QPainter(self.canvas)
        painter.setPen(QPen(Qt.blue, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        prev_point = None
        for point in signature_points:
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

    def show_about(self):
        """顯示關於資訊"""
        QMessageBox.information(self, "About", "This is a signature verification and restoration tool.")

    def resizeEvent(self, event):
        """當視窗大小改變時，自適應畫布大小"""
        new_width = self.width() - 50
        new_height = int(self.height() / 2)

        self.canvas = QPixmap(new_width, new_height)
        self.canvas.fill(Qt.white)
        self.canvas_label.setPixmap(self.canvas)

        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignatureDecoder()
    window.show()
    sys.exit(app.exec_())
