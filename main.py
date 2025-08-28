# -*- coding: utf-8 -*-
"""
@Project: pytqt5Project
@File: main.py
@Author: 杜塞米
@CreateDate: 2025/8/27
@LastEditTime: 
@Description: 
@Version: 1.0
"""
# 1. 导入必要的模块
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)


# 2. 定义主窗口类，继承自 QMainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        # 调用父类的构造函数
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle("分布式光纤温度监测系统")
        # 设置窗口初始大小
        self.setGeometry(100, 100, 1600, 900)  # x, y, width, height


        # # --- 创建界面组件 ---
        # # 创建一个标签 (Label)
        # self.label = QLabel("Hello, World!")
        #
        # # 创建一个按钮 (Button)
        # self.button = QPushButton("点我")
        #
        # # --- 绑定事件 ---
        # # 将按钮的 "clicked" 信号连接到 "on_button_clicked" 方法（槽）
        # self.button.clicked.connect(self.on_button_clicked)
        #
        # # --- 设置布局 ---
        # # 创建一个垂直布局管理器
        # layout = QVBoxLayout()
        # # 将标签和按钮添加到布局中
        # layout.addWidget(self.label)
        # layout.addWidget(self.button)
        #
        # # 创建一个中央小部件 (central widget)，因为 QMainWindow 需要一个中央小部件
        # central_widget = QWidget()
        # # 将布局应用到这个中央小部件上
        # central_widget.setLayout(layout)
        #
        # # 将这个设置好布局的中央小部件设置为主窗口的中央小部件
        # self.setCentralWidget(central_widget)

    # 3. 定义按钮点击后要执行的方法（槽函数）
    def on_button_clicked(self):
        # 修改标签的文本
        self.label.setText("你好, PyQt!")
        print("按钮被点击了！")  # 也会在PyCharm的控制台打印信息


# 4. 应用程序的入口
if __name__ == '__main__':
    # 创建一个 QApplication 实例，它是 PyQt 应用的入口
    app = QApplication(sys.argv)

    # 创建主窗口的实例
    window = MainWindow()
    # 显示窗口
    window.show()

    # 启动应用程序的事件循环，并确保程序可以干净地退出
    sys.exit(app.exec())