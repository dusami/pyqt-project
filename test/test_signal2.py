# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: test_signal2.py
@Author: 杜塞米
@CreateDate: 2025/9/9
@LastEditTime: 
@Description: 
@Version: 1.0
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal


class SimpleDemo(QMainWindow):
    # 定义一个自定义信号，可以传递字符串参数
    custom_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("自定义信号Demo")
        self.setGeometry(300, 300, 400, 200)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建布局
        layout = QVBoxLayout()

        # 创建按钮
        self.button = QPushButton("发射自定义信号")

        # 创建标签
        self.label = QLabel("等待信号...")

        # 将自定义信号连接到槽函数
        self.custom_signal.connect(self.on_custom_signal)

        # 将按钮点击连接到发射自定义信号
        self.button.clicked.connect(self.emit_custom_signal)

        # 将部件添加到布局
        layout.addWidget(self.button)
        layout.addWidget(self.label)

        # 设置布局
        central_widget.setLayout(layout)

        # 计数器
        self.click_count = 0

    def emit_custom_signal(self):
        # 发射自定义信号，附带计数信息
        self.click_count += 1
        message = f"第{self.click_count}次发射信号!"
        self.custom_signal.emit(message)

    def on_custom_signal(self, message):
        # 这是槽函数，当自定义信号发出时会执行
        self.label.setText(f"收到信号: {message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleDemo()
    window.show()
    sys.exit(app.exec_())