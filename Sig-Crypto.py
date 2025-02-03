import sys
import os
import hashlib
import json
import base64
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel, QCheckBox, QComboBox, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint, QTimer

class SignaturePad(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Message & Signature Hasher")
        self.setFixedSize(850, 750)

        # 畫布設定
        self.canvas_width = self.width() - 50  # 讓畫布與視窗寬度匹配
        self.canvas_height = 400
        self.canvas = QPixmap(self.canvas_width, self.canvas_height)
        self.canvas.fill(Qt.white)
        self.signature_points = []
        self.latest_hash = None  

        # 確保資料夾存在
        self.ensure_directories()

        # 顯示滑鼠座標 & 時間
        self.mouse_position_label = QLabel("Mouse Position: (0, 0)", self)
        self.time_label = QLabel("Time: " + self.get_current_time(), self)

        # 設定計時器，每秒更新時間
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # 選項：去除背景 & Hash 格式
        self.remove_background_checkbox = QCheckBox("Remove Background", self)
        self.remove_background_checkbox.setChecked(True)

        self.hash_format_combo = QComboBox(self)
        self.hash_format_combo.addItems(["JSON", "CSV", "TXT"])
        self.hash_format_combo.setCurrentIndex(0)

        # 顯示畫布
        self.canvas_label = QLabel(self)
        self.canvas_label.setPixmap(self.canvas)

        # 設定 GUI 元件
        self.message_input = QTextEdit(self)
        self.message_input.setPlaceholderText("Enter your message here...")

        self.clear_button = QPushButton("Clear Signature", self)
        self.clear_button.clicked.connect(self.clear_signature)

        self.generate_button = QPushButton("Generate Hash & Save Files")
        self.generate_button.clicked.connect(self.generate_hash)

        self.signature_display = QTextEdit(self)
        self.signature_display.setReadOnly(True)

        self.label_sign = QLabel("Sign Below:", self)
        self.label_output = QLabel("Generated Hash:", self)

        # 水平佈局（滑鼠座標 + 當前時間）
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.mouse_position_label)
        info_layout.addWidget(self.time_label)

        # 水平佈局（Hash 格式選擇 & 是否去背景）
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(self.remove_background_checkbox)
        settings_layout.addWidget(QLabel("Save Hash As:"))
        settings_layout.addWidget(self.hash_format_combo)

        # 佈局
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(self.message_input)
        layout.addLayout(info_layout)
        layout.addWidget(self.label_sign)
        layout.addWidget(self.canvas_label)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.generate_button)
        layout.addLayout(settings_layout)
        layout.addWidget(self.label_output)
        layout.addWidget(self.signature_display)
        self.setLayout(layout)

        self.drawing = False
        self.last_point = QPoint()

    def ensure_directories(self):
        """ 確保 'Signature_Image' 和 'Generated_Hash' 目錄存在 """
        os.makedirs("Signature_Image", exist_ok=True)
        os.makedirs("Generated_Hash", exist_ok=True)

    def get_current_time(self):
        """ 取得當前時間，格式為 YYYY:MM:DD:HH:MM:SS (24 小時制) """
        return datetime.now().strftime("%Y:%m:%d:%H:%M:%S")

    def get_long_timestamp(self):
        """ 取得長數列的時間戳，單位為微秒 """
        return str(int(datetime.utcnow().timestamp() * 1e6))

    def update_time(self):
        """ 每秒更新當前時間 """
        self.time_label.setText("Time: " + self.get_current_time())

    def closeEvent(self, event):
        """ 關閉視窗時的確認對話框 """
        reply = QMessageBox.question(self, "Exit Confirmation",
                                     "Are you sure you want to exit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def paintEvent(self, event):
        """ 確保畫布在 UI 上正確顯示 """
        self.canvas_label.setPixmap(self.canvas)

    def mousePressEvent(self, event):
        """ 滑鼠點擊開始簽名 """
        if event.button() == Qt.LeftButton and self.canvas_label.geometry().contains(event.pos()):
            self.drawing = True
            self.last_point = event.pos() - self.canvas_label.pos()
            timestamp = self.get_long_timestamp()
            self.signature_points.append({"X": self.last_point.x(), "Y": self.last_point.y(), "Timestamp": timestamp})

    def mouseMoveEvent(self, event):
        """ 滑鼠移動時畫線 """
        if self.drawing and event.buttons() & Qt.LeftButton and self.canvas_label.geometry().contains(event.pos()):
            painter = QPainter(self.canvas)
            painter.setPen(QPen(Qt.black, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            new_point = event.pos() - self.canvas_label.pos()
            painter.drawLine(self.last_point, new_point)
            self.last_point = new_point
            timestamp = self.get_long_timestamp()
            self.signature_points.append({"X": new_point.x(), "Y": new_point.y(), "Timestamp": timestamp})
            self.update()

    def mouseReleaseEvent(self, event):
        """ 滑鼠放開時，結束簽名 """
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def generate_hash(self):
        """ 產生 SHA-256 Hash 並儲存 JSON & 簽名圖片 """
        message = self.message_input.toPlainText().strip()
        if not message:
            self.signature_display.setText("Error: Message cannot be empty!")
            return

        timestamp = self.get_long_timestamp()  
        filename = f"Generated_Hash/{timestamp}"

        data = {
            "Message": message,
            "Sign_Coor_X": [p["X"] for p in self.signature_points],
            "Sign_Coor_Y": [p["Y"] for p in self.signature_points],
            "Timestamp": [p["Timestamp"] for p in self.signature_points],
            "Hash": base64.b64encode(hashlib.sha256(json.dumps(self.signature_points).encode()).digest()).decode()
        }

        # 儲存 Hash
        format_selected = self.hash_format_combo.currentText()
        if format_selected == "JSON":
            with open(f"{filename}.json", "w") as f:
                json.dump(data, f, indent=4)

        # 儲存圖片
        image_filename = f"Signature_Image/{timestamp}.png"
        self.canvas.save(image_filename, "PNG")

        # 更新顯示 Hash 並彈出成功對話框
        self.latest_hash = data
        self.signature_display.setText(json.dumps(data, indent=4))

        QMessageBox.information(self, "Success", "Hash and Signature Image saved successfully!")

    def clear_signature(self):
        """ 清除畫布 """
        self.canvas.fill(Qt.white)
        self.signature_points = []
        self.latest_hash = None
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignaturePad()
    window.show()
    sys.exit(app.exec_())
