# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: coeff_calibration_dialog.py
@Author: 杜塞米
@CreateDate: 2026/1/7
@LastEditTime: 
@Description: 
@Version: 1.0
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QGroupBox, QListWidget,
                             QListWidgetItem, QGridLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QWidget, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSlot


class FiberCoeffCalibrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("光纤校准系数")
        self.resize(850, 550)  # 根据图片适当调整窗口大小

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        # --- 主布局：水平分割 (左侧列表 | 右侧内容) ---
        main_layout = QHBoxLayout()

        # ================= 左侧：DTS测温通道列表 =================
        channel_group = QGroupBox("DTS测温通道")
        channel_layout = QVBoxLayout()

        self.channel_list = QListWidget()
        self.channel_list.setFixedWidth(180)

        # 添加8个通道
        for i in range(1, 9):
            item = QListWidgetItem(f"测温通道{i}")
            # 设置一些图标或对其方式可以更像原图，这里保持简洁
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.channel_list.addItem(item)

        # 默认选中第一个通道
        self.channel_list.setCurrentRow(0)

        channel_layout.addWidget(self.channel_list)
        channel_group.setLayout(channel_layout)

        main_layout.addWidget(channel_group)

        # ================= 右侧：参数配置区域 =================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # --- 1. 顶部：温度标定参数 (GroupBox) ---
        gb_params = QGroupBox("温度标定参数")
        # GroupBox 内部布局：左边是输入框，右边是增删按钮
        gb_inner_layout = QHBoxLayout()

        # --- 1.1 左边输入框区域 (Grid Layout) ---
        input_widget = QWidget()
        grid = QGridLayout(input_widget)
        grid.setSpacing(10)  # 控件间距

        # 第一行：分段长度
        grid.addWidget(QLabel("分段长度"), 0, 0)
        self.le_segment_len = QLineEdit("4000.0")
        grid.addWidget(self.le_segment_len, 0, 1)
        grid.addWidget(QLabel("米 (光纤截止的长度)"), 0, 2, 1, 2)  # 跨两列

        # 第二行：折射率 & 敏感系数
        grid.addWidget(QLabel("光纤折射率"), 1, 0)
        self.le_refractive = QLineEdit("1.4640")
        grid.addWidget(self.le_refractive, 1, 1)

        grid.addWidget(QLabel("温度敏感系数"), 1, 2)
        self.le_sensitivity = QLineEdit("633.0")  # 假设图片里的数值
        grid.addWidget(self.le_sensitivity, 1, 3)

        # 第三行：衰减系数 & 补偿值
        grid.addWidget(QLabel("光纤衰减系数"), 2, 0)
        self.le_attenuation = QLineEdit("0.0800")
        grid.addWidget(self.le_attenuation, 2, 1)

        grid.addWidget(QLabel("温度补偿值"), 2, 2)
        self.le_offset = QLineEdit("1.0")
        grid.addWidget(self.le_offset, 2, 3)

        gb_inner_layout.addWidget(input_widget)

        # --- 1.2 右边按钮区域 (Vertical) ---
        btn_widget = QWidget()
        vbox_btns = QVBoxLayout(btn_widget)
        vbox_btns.addStretch()  # 上面顶住

        self.btn_add = QPushButton("<= 增加")
        self.btn_delete = QPushButton("删除 =>")

        vbox_btns.addWidget(self.btn_add)
        vbox_btns.addWidget(self.btn_delete)

        vbox_btns.addStretch()  # 下面顶住
        gb_inner_layout.addWidget(btn_widget)

        gb_params.setLayout(gb_inner_layout)
        right_layout.addWidget(gb_params)

        # --- 2. 中部：数据表格 (TableWidget) ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "分段终点(m)", "光纤折射率", "衰减系数", "敏感系数", "温度补偿值"
        ])

        # 表格样式调整
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列宽自适应
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选中整行
        self.table.setAlternatingRowColors(True)  # 隔行变色

        right_layout.addWidget(self.table)

        # --- 3. 底部：保存与退出按钮 ---
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()  # 靠右对齐

        self.btn_save = QPushButton("保存设置")
        self.btn_save.setMinimumHeight(30)
        self.btn_exit = QPushButton("退出")
        self.btn_exit.setMinimumHeight(30)

        bottom_layout.addWidget(self.btn_save)
        bottom_layout.addWidget(self.btn_exit)

        right_layout.addLayout(bottom_layout)

        # 将右侧组件加入主布局
        main_layout.addWidget(right_widget)
        self.setLayout(main_layout)

    def setup_connections(self):
        self.btn_exit.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_add.clicked.connect(self.on_add_row)
        self.btn_delete.clicked.connect(self.on_delete_row)

    @pyqtSlot()
    def on_add_row(self):
        """点击增加按钮，将上面的参数添加到表格中"""
        # 获取输入框的值
        seg_len = self.le_segment_len.text()
        refractive = self.le_refractive.text()
        attenuation = self.le_attenuation.text()
        sensitivity = self.le_sensitivity.text()
        offset = self.le_offset.text()

        # 简单的非空校验 (可选)
        if not seg_len: return

        # 插入新行
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)

        # 填入数据
        self.table.setItem(row_idx, 0, QTableWidgetItem(seg_len))
        self.table.setItem(row_idx, 1, QTableWidgetItem(refractive))
        self.table.setItem(row_idx, 2, QTableWidgetItem(attenuation))
        self.table.setItem(row_idx, 3, QTableWidgetItem(sensitivity))
        self.table.setItem(row_idx, 4, QTableWidgetItem(offset))

    @pyqtSlot()
    def on_delete_row(self):
        """点击删除按钮，删除当前选中的行"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
        else:
            print("请先选择要删除的行")

    @pyqtSlot()
    def on_save(self):
        """遍历表格获取所有数据并保存"""
        data = []
        rows = self.table.rowCount()
        cols = self.table.columnCount()

        for r in range(rows):
            row_data = []
            for c in range(cols):
                item = self.table.item(r, c)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        current_channel = self.channel_list.currentItem().text()
        print(f"保存 [{current_channel}] 的数据: {data}")

        self.accept()