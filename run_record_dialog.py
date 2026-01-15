# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: run_record_dialog.py.py
@Author: 杜塞米
@CreateDate: 2026/1/15
@LastEditTime: 
@Description: 
@Version: 1.0
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QCheckBox, QFileDialog,
                             QWidget, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSlot


class RunRecordSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("运行记录设置")
        self.resize(450, 300)  # 调整为适合的大小

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)  # 增加控件之间的垂直间距
        main_layout.setContentsMargins(30, 30, 30, 30)  # 设置窗口边距

        # --- 1. 保存测量数据 (主复选框) ---
        self.cb_save_data = QCheckBox("保存测量数据")
        self.cb_save_data.setChecked(True)  # 默认勾选
        main_layout.addWidget(self.cb_save_data)

        # --- 子选项区域 (缩进显示) ---
        # 创建一个 Widget 来容器化下面两行，方便做缩进或整体禁用
        self.sub_options_widget = QWidget()
        sub_layout = QVBoxLayout(self.sub_options_widget)
        sub_layout.setContentsMargins(20, 0, 0, 0)  # 左侧缩进 20px
        sub_layout.setSpacing(10)

        # 1.1 数据保存间隔
        h_layout_interval = QHBoxLayout()
        h_layout_interval.addWidget(QLabel("数据保存间隔"))
        self.le_interval = QLineEdit("50")
        self.le_interval.setFixedWidth(100)  # 限制宽度
        h_layout_interval.addWidget(self.le_interval)
        h_layout_interval.addStretch()  # 弹簧
        sub_layout.addLayout(h_layout_interval)

        # 1.2 数据保存目录
        h_layout_path = QHBoxLayout()
        h_layout_path.addWidget(QLabel("数据保存目录"))
        self.le_path = QLineEdit("D:\\")
        self.btn_browse = QPushButton("...")
        self.btn_browse.setFixedWidth(30)

        h_layout_path.addWidget(self.le_path)
        h_layout_path.addWidget(self.btn_browse)
        sub_layout.addLayout(h_layout_path)

        main_layout.addWidget(self.sub_options_widget)

        # --- 2. 其他复选框 ---
        # self.cb_save_alarm = QCheckBox("保存报警信息")
        # self.cb_save_alarm.setChecked(True)
        # main_layout.addWidget(self.cb_save_alarm)
        #
        # self.cb_save_run_info = QCheckBox("保存设备运行信息")
        # self.cb_save_run_info.setChecked(True)
        # main_layout.addWidget(self.cb_save_run_info)

        # --- 3. 底部确定按钮 ---
        main_layout.addStretch()  # 将按钮推到底部

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()  # 按钮靠右
        self.btn_ok = QPushButton("确定")
        self.btn_ok.setFixedSize(80, 30)
        btn_layout.addWidget(self.btn_ok)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def setup_connections(self):
        # 浏览按钮
        self.btn_browse.clicked.connect(self.select_directory)
        # 确定按钮
        self.btn_ok.clicked.connect(self.on_save)
        # 联动逻辑：如果取消勾选"保存测量数据"，则下面的输入框变灰
        self.cb_save_data.toggled.connect(self.toggle_sub_options)

    @pyqtSlot()
    def select_directory(self):
        """打开文件夹选择框"""
        # QFileDialogs是QT提供的系统文件对话框
        # getExistingDiretory()是专门用来选择文件夹的函数
        directory = QFileDialog.getExistingDirectory(self, "选择保存目录", self.le_path.text())
        #self为父窗口，对话框会依附在主窗口上；第三个参数是默认打开路径
        if directory:
            # 替换斜杠为 Windows 风格，\\代表一个真正的反斜杠
            directory = directory.replace("/", "\\")
            self.le_path.setText(directory)

    @pyqtSlot(bool)
    def toggle_sub_options(self, checked):
        """根据主复选框的状态，启用/禁用子选项"""
        self.sub_options_widget.setEnabled(checked)

    @pyqtSlot()
    def on_save(self):
        """保存配置"""
        config = {
            "save_data": self.cb_save_data.isChecked(),
            "interval": self.le_interval.text(),
            "path": self.le_path.text(),
            "save_alarm": self.cb_save_alarm.isChecked(),
            "save_run_info": self.cb_save_run_info.isChecked()
        }
        print(f"运行记录配置已保存: {config}")
        self.accept()