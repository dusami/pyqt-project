# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: test _signal.py
@Author: 杜塞米
@CreateDate: 2025/9/9
@LastEditTime: 
@Description: 
@Version: 1.0
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QLineEdit, QSpinBox, QComboBox,
                             QGroupBox, QTextEdit, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class CustomSignalEmitter(QWidget):
    """自定义信号发射器类"""
    # 定义一个自定义信号，可以传递字符串参数
    custom_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 创建一个按钮来发射自定义信号
        self.emit_btn = QPushButton("发射自定义信号")
        self.emit_btn.clicked.connect(self.emit_custom_signal)
        layout.addWidget(self.emit_btn)

        self.setLayout(layout)

    def emit_custom_signal(self):
        # 发射自定义信号，附带当前时间作为参数
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.custom_signal.emit(f"自定义信号在 {current_time} 被触发!")


class SignalSlotDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 信号与槽机制演示")
        self.setGeometry(300, 200, 800, 600)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        layout = QVBoxLayout(central_widget)

        # 添加标题
        title = QLabel("PyQt5 信号与槽机制")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 18, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # 创建说明区域
        explanation = QTextEdit()
        explanation.setPlainText("""信号(Signal)和槽(Slot)是PyQt的核心机制，用于对象之间的通信。

信号：
- 当对象的状态改变时发出的通知
- 可以是内置信号(如按钮的clicked)或自定义信号

槽：
- 是对信号做出响应的方法
- 可以是任何可调用的Python函数

连接：
- 使用object.signal.connect(slot_function)将信号连接到槽
- 一个信号可以连接到多个槽
- 多个信号可以连接到一个槽""")
        explanation.setReadOnly(True)
        layout.addWidget(explanation)

        # 创建演示区域
        self.create_demo_area(layout)

        # 创建日志区域
        self.create_log_area(layout)

    def create_demo_area(self, parent_layout):
        # 创建水平布局放置演示组件
        demo_layout = QHBoxLayout()

        # 左侧：内置信号演示
        left_group = QGroupBox("内置信号演示")
        left_layout = QVBoxLayout()

        # 按钮点击信号
        self.btn = QPushButton("点击我!")
        self.btn.clicked.connect(self.on_button_clicked)
        left_layout.addWidget(self.btn)

        # 文本框文本改变信号
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("输入文本...")
        self.text_edit.textChanged.connect(self.on_text_changed)
        left_layout.addWidget(self.text_edit)

        # 组合框选项改变信号
        self.combo = QComboBox()
        self.combo.addItems(["选项1", "选项2", "选项3", "选项4"])
        self.combo.currentIndexChanged.connect(self.on_combo_changed)
        left_layout.addWidget(self.combo)

        left_group.setLayout(left_layout)
        demo_layout.addWidget(left_group)

        # 右侧：自定义信号演示
        right_group = QGroupBox("自定义信号演示")
        right_layout = QVBoxLayout()

        # 创建自定义信号发射器实例
        self.signal_emitter = CustomSignalEmitter()
        # 连接自定义信号到槽函数
        self.signal_emitter.custom_signal.connect(self.on_custom_signal)
        right_layout.addWidget(self.signal_emitter)

        right_group.setLayout(right_layout)
        demo_layout.addWidget(right_group)

        parent_layout.addLayout(demo_layout)

    def create_log_area(self, parent_layout):
        # 创建日志区域
        log_group = QGroupBox("事件日志")
        log_layout = QVBoxLayout()

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        log_layout.addWidget(self.log)

        # 添加清除按钮
        clear_btn = QPushButton("清除日志")
        clear_btn.clicked.connect(self.log.clear)
        log_layout.addWidget(clear_btn)

        log_group.setLayout(log_layout)
        parent_layout.addWidget(log_group)

    def on_button_clicked(self):
        self.log.append("按钮被点击了!")

        # 改变按钮文本和颜色
        self.btn.setText("再次点击!")
        palette = self.btn.palette()
        palette.setColor(QPalette.Button, QColor(200, 230, 255))
        self.btn.setPalette(palette)
        self.btn.setAutoFillBackground(True)

    def on_text_changed(self, text):
        self.log.append(f"文本改变: {text}")

    def on_combo_changed(self, index):
        self.log.append(f"组合框选择改变: 索引 {index}, 文本 '{self.combo.currentText()}'")

    def on_custom_signal(self, message):
        self.log.append(f"收到自定义信号: {message}")

        # 高亮显示日志中的自定义信号
        self.log.moveCursor(self.log.textCursor().End)
        self.log.setTextBackgroundColor(QColor(255, 255, 200))
        self.log.insertPlainText(" [自定义信号处理完毕] ")
        self.log.setTextBackgroundColor(QColor(255, 255, 255))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalSlotDemo()
    window.show()
    sys.exit(app.exec_())