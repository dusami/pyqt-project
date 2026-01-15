# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: measurement_param_dialog.py
@Author: 杜塞米
@CreateDate: 2026/1/7
@LastEditTime: 
@Description: 
@Version: 1.0
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QGroupBox, QRadioButton,
                             QComboBox, QListWidget, QListWidgetItem, QGridLayout,
                             QSpacerItem, QSizePolicy, QWidget)
from PyQt5.QtCore import Qt, pyqtSlot


class FiberMeasurementParamsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("计算参数设置")
        self.resize(750, 500)  # 根据图片比例设置初始大小

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        # --- 主布局：水平分割 (左侧列表 | 右侧设置) ---
        main_layout = QHBoxLayout()

        # ================= 左侧：通道列表 =================
        self.channel_list = QListWidget()
        self.channel_list.setFixedWidth(180)

        # 模拟图片中的8个通道
        for i in range(1, 9):
            item = QListWidgetItem(f"测温通道{i}")
            # 设置为可勾选
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # 默认未勾选，你可以根据需求修改
            item.setCheckState(Qt.Unchecked)
            self.channel_list.addItem(item)

        # 默认选中第一个条目（高亮）
        self.channel_list.setCurrentRow(0)
        # 让第一个条目打钩模拟图片
        self.channel_list.item(0).setCheckState(Qt.Checked)

        main_layout.addWidget(self.channel_list)

        # ================= 右侧：参数设置区域 =================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # --- 1. 分组框：光纤长度 ---
        gb_length = QGroupBox("光纤长度")
        gb_length_layout = QHBoxLayout()

        gb_length_layout.addWidget(QLabel("实际光纤长度从"))
        self.le_len_start = QLineEdit("0.0")
        gb_length_layout.addWidget(self.le_len_start)
        gb_length_layout.addWidget(QLabel("米 到"))
        self.le_len_end = QLineEdit("4000.0")
        gb_length_layout.addWidget(self.le_len_end)
        gb_length_layout.addWidget(QLabel("米"))

        gb_length.setLayout(gb_length_layout)
        right_layout.addWidget(gb_length)

        # --- 2. 分组框：运算参数 ---
        gb_calc = QGroupBox("运算参数")
        gb_calc_layout = QGridLayout()

        # 选项 A
        self.rb_accum_time = QRadioButton("根据测量时间")
        self.rb_accum_time.setChecked(True)  # 默认选中
        gb_calc_layout.addWidget(self.rb_accum_time, 0, 0)

        gb_calc_layout.addWidget(QLabel("估计光纤长度:"), 0, 1)
        self.le_est_len = QLineEdit("4150")
        gb_calc_layout.addWidget(self.le_est_len, 0, 2)
        gb_calc_layout.addWidget(QLabel("米"), 0, 3)

        gb_calc_layout.addWidget(QLabel("测量时间:"), 0, 4)
        self.le_accum_time = QLineEdit("5.0")
        gb_calc_layout.addWidget(self.le_accum_time, 0, 5)
        gb_calc_layout.addWidget(QLabel("秒"), 0, 6)

        # 选项 B
        self.rb_calc_param = QRadioButton("根据运算参数")
        gb_calc_layout.addWidget(self.rb_calc_param, 1, 0)

        gb_calc_layout.addWidget(QLabel("单次测量时间:"), 1, 1)
        self.le_single_time = QLineEdit("40")
        gb_calc_layout.addWidget(self.le_single_time, 1, 2)
        gb_calc_layout.addWidget(QLabel("us"), 1, 3)

        gb_calc_layout.addWidget(QLabel("平均次数:"), 1, 4)
        self.le_avg_count = QLineEdit("125000")
        gb_calc_layout.addWidget(self.le_avg_count, 1, 5)
        # 最后一列留空占位

        gb_calc.setLayout(gb_calc_layout)
        right_layout.addWidget(gb_calc)

        # --- 3. 分组框：光纤参数 ---
        gb_fiber = QGroupBox("光纤参数")
        gb_fiber_layout = QHBoxLayout()

        gb_fiber_layout.addWidget(QLabel("A探测分辨率"))
        self.cb_resolution1 = QComboBox()
        self.cb_resolution1.addItems(["2米 (20ns)", "1米 (10ns)", "0.5米 (5ns)"])
        gb_fiber_layout.addWidget(self.cb_resolution1)

        gb_fiber_layout.addWidget(QLabel("B探测分辨率"))
        self.cb_resolution2 = QComboBox()
        self.cb_resolution2.addItems(["2米 (20ns)", "1米 (10ns)", "0.5米 (5ns)"])
        gb_fiber_layout.addWidget(self.cb_resolution2)

        # 上面添加功能，把探测分辨率改成A和B

        gb_fiber_layout.addStretch()  # 弹簧，把后面的推到右边

        gb_fiber_layout.addWidget(QLabel("激光功率大小"))
        self.le_laser_power = QLineEdit("2000")
        self.le_laser_power.setFixedWidth(80)
        gb_fiber_layout.addWidget(self.le_laser_power)

        gb_fiber.setLayout(gb_fiber_layout)
        right_layout.addWidget(gb_fiber)

        # --- 4. 分组框道激光泵浦电流 ---
        gb_current = QGroupBox("泵浦电流")
        gb_current_layout = QHBoxLayout()

        gb_current_layout.addWidget(QLabel("A通道激光泵浦电流"))
        self.le_current1 = QLineEdit("800")
        gb_current_layout.addWidget(self.le_current1)
        gb_current_layout.addWidget(QLabel("b通道激光泵浦电流"))
        self.le_current2 = QLineEdit("800")
        gb_current_layout.addWidget(self.le_current2)

        gb_current.setLayout(gb_current_layout)
        right_layout.addWidget(gb_current)

        # --- 5. 底部按钮区 ---
        # "更新当前参数" 按钮似乎是独立的一行
        # update_layout = QHBoxLayout()
        # update_layout.addStretch()
        # self.btn_update = QPushButton("更新当前参数")
        # self.btn_update.setMinimumHeight(30)
        # update_layout.addWidget(self.btn_update)
        # right_layout.addLayout(update_layout)

        # 底部 "保存设置" 和 "退出"
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()  # 靠右对齐

        self.btn_save = QPushButton("保存设置")
        self.btn_save.setMinimumHeight(30)
        self.btn_exit = QPushButton("退出")
        self.btn_exit.setMinimumHeight(30)

        bottom_layout.addWidget(self.btn_save)
        bottom_layout.addWidget(self.btn_exit)

        right_layout.addStretch()  # 让上面的组件顶上去
        right_layout.addLayout(bottom_layout)

        # 将右侧整体放入主布局
        main_layout.addWidget(right_widget)
        self.setLayout(main_layout)

        # 初始化界面状态（处理灰显逻辑）
        self.on_mode_changed()

    def setup_connections(self):
        # 按钮连接
        self.btn_exit.clicked.connect(self.reject)  # 点击退出关闭窗口，reject是QDialog的方法，会 关闭窗口 并返回 QDialog.Rejected 状态
        self.btn_save.clicked.connect(self.on_save)
        # self.btn_update.clicked.connect(self.on_update)

        # 单选框逻辑连接：切换模式时禁用/启用输入框
        self.rb_accum_time.toggled.connect(self.on_mode_changed)
        self.rb_calc_param.toggled.connect(self.on_mode_changed)

    @pyqtSlot()
    def on_mode_changed(self):
        """根据单选框的状态，禁用或启用对应的输入框，还原图片中的灰显效果"""
        is_accum_mode = self.rb_accum_time.isChecked()

        # 模式1输入框
        self.le_est_len.setEnabled(is_accum_mode)
        self.le_accum_time.setEnabled(is_accum_mode)

        # 模式2输入框 (与模式1相反)
        self.le_single_time.setEnabled(not is_accum_mode)
        self.le_avg_count.setEnabled(not is_accum_mode)

    @pyqtSlot()
    def on_save(self):
        """点击保存设置"""
        # 1. 获取当前选中的通道
        checked_channels = []
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            if item.checkState() == Qt.Checked:
                checked_channels.append(item.text())

        # 2. 获取参数值
        length_start = self.le_len_start.text()
        length_end = self.le_len_end.text()

        print(f"保存设置: 通道={checked_channels}, 长度={length_start}-{length_end}")

        # 这里你可以添加校验逻辑，或者发射自定义信号把数据传回主界面
        self.accept()  # 关闭并返回 Accepted 状态

    # @pyqtSlot()
    # def on_update(self):
    #     print("点击了更新当前参数")