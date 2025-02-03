import sys
import os
import hashlib
import json
import base64
import numpy as np
import cv2
from datetime import datetime, timezone
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLabel, QCheckBox,
    QPushButton, QMenuBar, QAction, QMessageBox
)
from PyQt5.QtGui import QPainter, QPen, QPixmap, QIcon
from PyQt5.QtCore import Qt, QPoint, QTimer


class SignaturePad(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Message & Signature Hasher")
        self.setMinimumSize(850, 850)  # 設定最小視窗大小
        self.setWindowIcon(QIcon("icon.png"))

        # 畫布設定
        self.canvas = QPixmap(800, 400)  # 初始畫布大小
        self.canvas.fill(Qt.white)
        self.signature_points = []

        # 確保資料夾存在
        self.ensure_directories()

        # 設定 GUI 元件
        self.message_input = QTextEdit(self)
        self.message_input.setPlaceholderText("Enter your message here...")

        self.mouse_position_label = QLabel("Mouse Position: (0, 0)", self)
        self.current_time_label = QLabel("Time: " + self.get_current_time(), self)

        self.clear_button = QPushButton("Clear Signature", self)
        self.clear_button.clicked.connect(self.clear_signature)

        self.generate_button = QPushButton("Generate Hash & Save JSON")
        self.generate_button.clicked.connect(self.generate_hash)

        self.signature_display = QTextEdit(self)
        self.signature_display.setReadOnly(True)

        self.label_sign = QLabel("Sign Below:", self)

        self.remove_background_checkbox = QCheckBox("Remove White Background", self)
        self.remove_background_checkbox.setChecked(True)

        # 設定計時器，用於更新時間
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # 畫布顯示 Label
        self.canvas_label = QLabel(self)
        self.canvas_label.setPixmap(self.canvas)

        # 設置佈局
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(self.message_input)
        layout.addWidget(self.mouse_position_label)
        layout.addWidget(self.current_time_label)
        layout.addWidget(self.label_sign)
        layout.addWidget(self.canvas_label)
        layout.addWidget(self.remove_background_checkbox)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.generate_button)
        layout.addWidget(QLabel("Generated Hash (JSON):"))
        layout.addWidget(self.signature_display)
        self.setLayout(layout)

        self.drawing = False
        self.last_point = QPoint()

    def ensure_directories(self):
        os.makedirs("Signature_Image", exist_ok=True)
        os.makedirs("Generated_Hash", exist_ok=True)

    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_time(self):
        self.current_time_label.setText("Time: " + self.get_current_time())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.canvas_label.geometry().contains(event.pos()):
            self.drawing = True
            self.last_point = event.pos() - self.canvas_label.pos()
            self.signature_points = [{"X": self.last_point.x(), "Y": self.last_point.y()}]

    def mouseMoveEvent(self, event):
        if self.canvas_label.geometry().contains(event.pos()):
            canvas_x = event.x() - self.canvas_label.x()
            canvas_y = self.canvas.height() - (event.y() - self.canvas_label.y())
            self.mouse_position_label.setText(f"Mouse Position: ({canvas_x}, {canvas_y})")

        if self.drawing and event.buttons() & Qt.LeftButton:
            painter = QPainter(self.canvas)
            painter.setPen(QPen(Qt.blue, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            new_point = event.pos() - self.canvas_label.pos()
            painter.drawLine(self.last_point, new_point)
            self.signature_points.append({"X": new_point.x(), "Y": new_point.y()})
            self.last_point = new_point
            self.update()
            self.canvas_label.setPixmap(self.canvas)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def clear_signature(self):
        self.canvas.fill(Qt.white)
        self.signature_points = []
        self.canvas_label.setPixmap(self.canvas)

    def remove_white_background(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        white_mask = np.all(image[:, :, :3] == [255, 255, 255], axis=-1)
        image[white_mask, 3] = 0
        return image

    def save_signature_image(self, filename):
        image = self.canvas.toImage()
        buffer = image.bits().asarray(self.canvas.width() * self.canvas.height() * 4)
        img_array = np.array(buffer, dtype=np.uint8).reshape((self.canvas.height(), self.canvas.width(), 4))

        if self.remove_background_checkbox.isChecked():
            img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
            img_array = self.remove_white_background(img_array)
            cv2.imwrite(filename, img_array)
        else:
            self.canvas.save(filename, "PNG")

    def generate_hash(self):
        message = self.message_input.toPlainText().strip()

        if not message:
            QMessageBox.warning(self, "Error", "Message cannot be empty!")
            return

        if not self.signature_points:
            QMessageBox.warning(self, "Error", "You must provide a signature!")
            return

        timestamp = str(int(datetime.now(timezone.utc).timestamp() * 1e6))
        hash_data = {
            "Message": message,
            "Timestamp": timestamp,
            "Signature": self.signature_points,
            "Hash": base64.b64encode(hashlib.sha256(json.dumps(self.signature_points).encode()).digest()).decode()
        }

        file_name = f"Generated_Hash/{timestamp}.json"
        with open(file_name, "w") as f:
            json.dump(hash_data, f, indent=4)

        image_file_name = f"Signature_Image/{timestamp}.png"
        self.save_signature_image(image_file_name)

        self.signature_display.setText(json.dumps(hash_data, indent=4))
        QMessageBox.information(self, "Success", "Your signature has been saved, and the hash has been stored in JSON format.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))
    window = SignaturePad()
    window.show()
    sys.exit(app.exec_())
