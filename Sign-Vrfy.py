import sys
import json
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QFileDialog, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

class SignatureDecoder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signature Decoder")
        self.setGeometry(200, 200, 900, 500)

        # 介面組件
        self.load_button = QPushButton("Load Signature JSON", self)
        self.load_button.clicked.connect(self.load_signature)

        self.save_button = QPushButton("Save Restored Signature", self)
        self.save_button.clicked.connect(self.save_signature)
        self.save_button.setEnabled(False)

        self.canvas_label = QLabel(self)
        self.canvas = QPixmap(800, 400)
        self.canvas.fill(Qt.white)
        self.canvas_label.setPixmap(self.canvas)

        # 佈局
        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.canvas_label)
        self.setLayout(layout)

    def load_signature(self):
        """讀取簽名 JSON 檔案並繪製簽名"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Signature JSON", "", "JSON Files (*.json)")
        if not file_path:
            return

        with open(file_path, "r") as file:
            data = json.load(file)

        if "Signature" not in data:
            return

        signature_points = data["Signature"]

        # 重新繪製簽名
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
        self.save_button.setEnabled(True)

    def save_signature(self):
        """將還原的簽名存為圖片"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Signature Image", "", "PNG Files (*.png)")
        if file_path:
            self.canvas.save(file_path, "PNG")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignatureDecoder()
    window.show()
    sys.exit(app.exec_())
