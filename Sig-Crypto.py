import sys
import os
import hashlib
import json
import base64
import numpy as np
import cv2
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLabel, QCheckBox, QComboBox,
    QPushButton, QMenuBar, QAction, QMessageBox
)
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint


class SignaturePad(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Message & Signature Hasher")
        self.setFixedSize(850, 800)

        # 畫布設定
        self.canvas_width = self.width() - 50
        self.canvas_height = 400
        self.canvas = QPixmap(self.canvas_width, self.canvas_height)
        self.canvas.fill(Qt.white)
        self.signature_points = []

        # 確保資料夾存在
        self.ensure_directories()

        # 設定功能表列
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("檔案(F)")
        edit_menu = menu_bar.addMenu("編輯(E)")
        help_menu = menu_bar.addMenu("說明(H)")

        # 檔案選項
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 編輯選項
        clear_action = QAction("清除畫布", self)
        clear_action.triggered.connect(self.clear_signature)
        edit_menu.addAction(clear_action)

        # 說明選項
        about_action = QAction("關於", self)
        about_action.triggered.connect(self.show_about_info)
        help_menu.addAction(about_action)

        # 設定 GUI 元件
        self.message_input = QTextEdit(self)
        self.message_input.setPlaceholderText("Enter your message here...")

        self.mouse_position_label = QLabel("Mouse Position: (0, 0)", self)

        self.clear_button = QPushButton("Clear Signature", self)
        self.clear_button.clicked.connect(self.clear_signature)

        self.generate_button = QPushButton("Generate Hash & Save Files")
        self.generate_button.clicked.connect(self.generate_hash)

        self.signature_display = QTextEdit(self)
        self.signature_display.setReadOnly(True)

        self.label_sign = QLabel("Sign Below:", self)

        self.remove_background_checkbox = QCheckBox("Remove White Background", self)
        self.remove_background_checkbox.setChecked(True)

        self.hash_format_combo = QComboBox(self)
        self.hash_format_combo.addItems(["JSON", "CSV", "TXT"])
        self.hash_format_combo.setCurrentIndex(0)

        # 畫布顯示 Label
        self.canvas_label = QLabel(self)
        self.canvas_label.setPixmap(self.canvas)

        # 設置佈局
        layout = QVBoxLayout()
        layout.setMenuBar(menu_bar)
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(self.message_input)
        layout.addWidget(self.mouse_position_label)
        layout.addWidget(self.label_sign)
        layout.addWidget(self.canvas_label)
        layout.addWidget(self.remove_background_checkbox)
        layout.addWidget(QLabel("Select Hash Format:"))
        layout.addWidget(self.hash_format_combo)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.generate_button)
        layout.addWidget(QLabel("Generated Hash:"))
        layout.addWidget(self.signature_display)
        self.setLayout(layout)

        self.drawing = False
        self.last_point = QPoint()

    def ensure_directories(self):
        os.makedirs("Signature_Image", exist_ok=True)
        os.makedirs("Generated_Hash", exist_ok=True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.canvas_label.geometry().contains(event.pos()):
            self.drawing = True
            self.last_point = event.pos() - self.canvas_label.pos()
            # 初始化簽名點
            self.signature_points = [{"X": self.last_point.x(), "Y": self.last_point.y()}]

    def mouseMoveEvent(self, event):
        if self.canvas_label.geometry().contains(event.pos()):
            canvas_x = event.x() - self.canvas_label.x()
            canvas_y = self.canvas_height - (event.y() - self.canvas_label.y())
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

    def show_about_info(self):
        QMessageBox.information(self, "About", "This is a signature hashing application.")

    def remove_white_background(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        white_mask = np.all(image[:, :, :3] == [255, 255, 255], axis=-1)
        image[white_mask, 3] = 0
        return image

    def save_signature_image(self, filename):
        image = self.canvas.toImage()
        buffer = image.bits().asarray(self.canvas_width * self.canvas_height * 4)
        img_array = np.array(buffer, dtype=np.uint8).reshape((self.canvas_height, self.canvas_width, 4))

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

        timestamp = str(int(datetime.utcnow().timestamp() * 1e6))
        file_format = self.hash_format_combo.currentText()
        hash_data = {
            "Message": message,
            "Timestamp": timestamp,
            "Signature": self.signature_points,
            "Hash": base64.b64encode(hashlib.sha256(json.dumps(self.signature_points).encode()).digest()).decode()
        }

        file_name = f"Generated_Hash/{timestamp}.{file_format.lower()}"
        if file_format == "JSON":
            with open(file_name, "w") as f:
                json.dump(hash_data, f, indent=4)
        elif file_format == "CSV":
            with open(file_name, "w") as f:
                f.write("Key,Value\n")
                for key, value in hash_data.items():
                    f.write(f"{key},{value}\n")
        elif file_format == "TXT":
            with open(file_name, "w") as f:
                for key, value in hash_data.items():
                    f.write(f"{key}: {value}\n")

        image_file_name = f"Signature_Image/{timestamp}.png"
        self.save_signature_image(image_file_name)

        self.signature_display.setText(json.dumps(hash_data, indent=4))
        QMessageBox.information(self, "Success", f"Hash and Signature saved as {file_format}!")

    def closeEvent(self, event):
        """ 確認是否關閉視窗 """
        reply = QMessageBox.question(
            self, "Confirm Exit", "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignaturePad()
    window.show()
    sys.exit(app.exec_())
