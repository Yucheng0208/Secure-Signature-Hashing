import sys
import os
import hashlib
import json
import base64
import numpy as np
import cv2
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel, QCheckBox, QComboBox, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage
from PyQt5.QtCore import Qt, QPoint, QTimer

class SignaturePad(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Message & Signature Hasher")
        self.setFixedSize(850, 750)

        # 畫布設定
        self.canvas_width = self.width() - 50  
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
        self.remove_background_checkbox = QCheckBox("Remove White Background", self)
        self.remove_background_checkbox.setChecked(True)

        self.hash_format_combo = QComboBox(self)
        self.hash_format_combo.addItems(["JSON", "CSV", "TXT"])
        self.hash_format_combo.setCurrentIndex(0)

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

        # 畫布顯示 Label
        self.canvas_label = QLabel(self)
        self.canvas_label.setPixmap(self.canvas)

        # 佈局
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(self.message_input)
        layout.addWidget(self.mouse_position_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.label_sign)
        layout.addWidget(self.canvas_label)  # 確保畫布顯示
        layout.addWidget(self.clear_button)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.remove_background_checkbox)
        layout.addWidget(self.hash_format_combo)
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
            painter.setPen(QPen(Qt.blue, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))  # 筆跡變藍色
            new_point = event.pos() - self.canvas_label.pos()
            painter.drawLine(self.last_point, new_point)
            self.last_point = new_point
            timestamp = self.get_long_timestamp()
            self.signature_points.append({"X": new_point.x(), "Y": new_point.y(), "Timestamp": timestamp})
            self.update()
            self.canvas_label.setPixmap(self.canvas)  # 確保畫布更新

    def mouseReleaseEvent(self, event):
        """ 滑鼠放開時，結束簽名 """
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def clear_signature(self):
        """ 清除畫布 """
        self.canvas.fill(Qt.white)
        self.signature_points = []
        self.latest_hash = None
        self.canvas_label.setPixmap(self.canvas)  # 確保畫布更新

    def remove_white_background(self, image):
        """ 移除白色背景，使其透明 """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        white_mask = np.all(image[:, :, :3] == [255, 255, 255], axis=-1)
        image[white_mask, 3] = 0  # 讓白色變透明
        return image

    def save_signature_image(self, filename):
        """ 儲存簽名圖片，並根據選擇去除白色背景 """
        image = self.canvas.toImage()
        buffer = image.bits().asarray(self.canvas_width * self.canvas_height * 4)
        img_array = np.array(buffer, dtype=np.uint8).reshape((self.canvas_height, self.canvas_width, 4))

        if self.remove_background_checkbox.isChecked():
            img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)  # 轉換為 BGR
            img_array = self.remove_white_background(img_array)  # 去除白色背景
            cv2.imwrite(filename, img_array)
        else:
            self.canvas.save(filename, "PNG")

    def generate_hash(self):
        """ 產生 SHA-256 Hash 並儲存 JSON & 簽名圖片 """
        message = self.message_input.toPlainText().strip()
        if not message:
            self.signature_display.setText("Error: Message cannot be empty!")
            return

        timestamp = self.get_long_timestamp()  
        filename = f"Generated_Hash/{timestamp}.json"

        data = {
            "Message": message,
            "Sign_Coor_X": [p["X"] for p in self.signature_points],
            "Sign_Coor_Y": [p["Y"] for p in self.signature_points],
            "Timestamp": [p["Timestamp"] for p in self.signature_points],
            "Hash": base64.b64encode(hashlib.sha256(json.dumps(self.signature_points).encode()).digest()).decode()
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

        image_filename = f"Signature_Image/{timestamp}.png"
        self.save_signature_image(image_filename)

        self.latest_hash = data
        self.signature_display.setText(json.dumps(data, indent=4))

        QMessageBox.information(self, "Success", "Hash and Signature Image saved successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignaturePad()
    window.show()
    sys.exit(app.exec_())
