# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: main_app.py
@Author: 杜塞米
@CreateDate: 2025/11/3
@LastEditTime: 
@Description: 
@Version: 1.0
"""
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QListWidget, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QHeaderView, QMenuBar, QAction, QStatusBar, QRadioButton, QMessageBox, QDialog
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSlot
from measurement_param_dialog import FiberMeasurementParamsDialog
from coeff_calibration_dialog import FiberCoeffCalibrationDialog
from run_record_dialog import RunRecordSettingsDialog
from network_manager import NetworkManager
from dataParser import DataParser

# 配置网络参数
MCU_IP = "192.168.100.10"  # MCU的IP地址
MCU_PORT = 5001             # MCU的通信端口

# 主界面窗口
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- 1. 基本窗口设置 ---
        self.setWindowTitle("分布式光纤温度监测系统 测试版1.0")
        # 设置一个较大的默认窗口尺寸,x, y, width, height
        # 这里可以设置本电脑分辨率的80%
        self.setGeometry(100, 100, 1200, 800)
        # 启动时最大化
        self.showMaximized()

        # --- 2. 创建UI组件 ---
        # 创建菜单栏和状态栏
        self._create_menu_bar()
        self._create_status_bar()

        # 主窗口中心布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 使用水平布局，将窗口分为左右两部分
        main_layout = QHBoxLayout(main_widget)

        # 创建左侧、右侧面板
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 7)  # 让右侧面板占据更多空间 (比例为7:1)

        # --- 3. 【核心】集成后台逻辑 ---
        # a.创建数据解析器和网络线程
        self.parser = DataParser()

        # b. 创建新的 NetworkManager 实例 (代替 NetworkThread)
        #    传入 self 作为父对象，当主窗口关闭时，它会自动被清理
        self.network_manager = NetworkManager(self.parser, self)

        # c.连接信号和槽（前后台能沟通的关键） ---
        # self.network_manager.connection_status.connect(self.update_status)

        self.parser.temperature_data_ready.connect(self.update_temperature_display)
        # self.parser.packet_saved.connect(self.on_packet_saved)

        # d.启动初始连接 (代替 network_thread.start())
        #   这是一个非阻塞调用
        self.network_manager.connect_to_host(MCU_IP, MCU_PORT)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        # --- 1. 创建“设备连接”下拉菜单 ---
        # 首先，我们添加一个名为“设备连接”的主菜单项
        connection_menu = menu_bar.addMenu("设备连接")

        # 然后，创建两个QAction（下拉框里的具体选项）
        connect_action = QAction("设备连接", self)
        disconnect_action = QAction("设备断开", self)

        # 将这两个Action添加到“设备连接”主菜单下
        connection_menu.addAction(connect_action)
        connection_menu.addAction(disconnect_action)

        # 将Action的triggered信号连接到对应的槽函数
        # 当用户点击“设备连接”选项时，会调用 self.connect_device 方法
        connect_action.triggered.connect(self.connect_device)
        # 当用户点击“设备断开”选项时，会调用 self.disconnect_device 方法
        disconnect_action.triggered.connect(self.disconnect_device)

        # --- 2. 创建“设备配置”下拉菜单 ---
        # 首先，我们添加一个名为“设备配置”的主菜单项
        config_menu = menu_bar.addMenu("设备配置")

        # 然后，创建两个QAction（下拉框里的具体选项）
        fiber_measurement_params_action = QAction("光纤测量参数", self)
        fiber_coefficient_calibration_action = QAction("光纤系数校准", self)

        # 将这两个Action添加到“设备配置”主菜单下
        config_menu.addAction(fiber_measurement_params_action)
        config_menu.addAction(fiber_coefficient_calibration_action)

        # 将Action的triggered信号连接到对应的槽函数
        fiber_measurement_params_action.triggered.connect(self.open_dialog_fiber_measurement_params)
        fiber_coefficient_calibration_action.triggered.connect(self.open_dialog_fiber_coefficient_calibration)

        # --- 3. 创建“保存数据”下拉菜单 ---
        record_menu = menu_bar.addMenu("保存数据")
        action_record_settings = QAction("保存数据", self)
        action_record_settings.triggered.connect(self.open_record_dialog)
        record_menu.addAction(action_record_settings)

        # --- 4. 创建其他顶层菜单 ---
        menus = ["显示设置", "权限管理", "运行记录", "报警分区及转发", "技术支持"]
        for menu_name in menus:
            menu_bar.addMenu(menu_name)

    def open_record_dialog(self):
        """弹出运行记录设置窗口"""
        dialog = RunRecordSettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 这里可以添加更新全局配置的逻辑
            pass

    def open_dialog_fiber_measurement_params(self):
        """打开光纤测量参数窗口"""
        # 实例化对话框，传入 self 作为父对象，这样弹窗会居中在主窗口
        dialog = FiberMeasurementParamsDialog(self)

        # 显示窗口
        # 方法 A: dialog.exec_() -> 模态窗口 (推荐)
        # 用户必须关闭这个窗口才能操作主界面，防止参数没配完就去点别的
        if dialog.exec_() == QDialog.Accepted:
            print("用户点击了保存/确定")

    def open_dialog_fiber_coefficient_calibration(self):
        """打开光纤系数校准窗口"""
        dialog = FiberCoeffCalibrationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            print("校准参数已保存")


    def connect_device(self):
        """处理点击“设备连接”菜单项的逻辑"""
        print("正在执行：设备连接...")
        # 在这里，你可以启动你的网络线程或调用其连接方法
        # 例如: self.network_thread.start() 或 self.network_thread.connect_to_server()
        self.statusBar.showMessage("正在连接设备...")

    def disconnect_device(self):
        """处理点击“设备断开”菜单项的逻辑"""
        print("正在执行：设备断开...")
        # 在这里，你可以停止你的网络线程
        # 例如: self.network_thread.stop()
        self.statusBar.showMessage("设备已断开。")
        pass

    def _create_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("设备连接状态: 192.168.100.123  设备连接正常")

    def _create_left_panel(self):
        """创建并返回左侧面板的QWidget"""
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
        layout.setSpacing(20)

        # 1. 通道列表(创建带标题的分组框)
        channel_group = QGroupBox("当前DTS主机:[Host1]")
        channel_layout = QVBoxLayout()
        # 创建一个列表控件用于显示通道列表
        self.channel_list = QListWidget()
        for i in range(1, 9):
            self.channel_list.addItem(f"  测量通道{i}")
        # 设置图标等可以后续添加
        channel_layout.addWidget(self.channel_list)
        channel_group.setLayout(channel_layout)

        # 2. 系统运行状态
        status_group = QGroupBox("系统运行状态")
        status_layout = QVBoxLayout()

        run_stop_layout = QHBoxLayout()
        run_button = QPushButton("运行")
        run_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        fault_button = QPushButton("故障")
        fault_button.setStyleSheet("padding: 10px;")
        run_stop_layout.addWidget(run_button)
        run_stop_layout.addWidget(fault_button)

        status_layout.addLayout(run_stop_layout)
        status_layout.addWidget(QLabel("系统状态及操作", alignment=Qt.AlignCenter))

        control_layout = QHBoxLayout()
        control_layout.addWidget(QPushButton("消音"))
        control_layout.addWidget(QPushButton("复位"))
        control_layout.addWidget(QPushButton("自检"))
        status_layout.addLayout(control_layout)
        status_group.setLayout(status_layout)

        # 3. 设备连接状态 (示例，可以是一个日志列表)
        connection_group = QGroupBox("设备连接状态")
        connection_layout = QVBoxLayout()
        self.connection_log = QListWidget()
        self.connection_log.addItem("1")
        self.connection_log.addItem("2")
        self.connection_log.addItem("3")
        connection_layout.addWidget(self.connection_log)
        connection_group.setLayout(connection_layout)

        # 将所有组件添加到左侧布局中
        layout.addWidget(channel_group, 2)  # 比例为2
        layout.addWidget(status_group, 1)  # 比例为1
        layout.addWidget(connection_group, 1)  # 比例为1

        return left_widget

    def _create_right_panel(self):
        # """创建并返回右侧面板的QWidget"""
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)

        # 1. 图表上方的图像缩放
        zoom_groupbox = QGroupBox()
        zoom_layout = QHBoxLayout()  # 用水平布局来排列单选按钮

        self.temp_start_button = QPushButton("温度监测开启")
        self.temp_end_button = QPushButton("温度监测暂停")

        self.rb_zoom_xy = QRadioButton("矩阵缩放")
        self.rb_zoom_x = QRadioButton("X轴缩放")
        self.rb_zoom_y = QRadioButton("Y轴缩放")
        self.rb_zoom_xy.setChecked(True)        # 设置“矩阵缩放”为默认选中状态

        self.help_button = QPushButton("...")
        # self.help_button.setFixedSize(25, 25)
        self.help_button.setToolTip("图形窗口快捷键说明")

        zoom_layout.addWidget(self.temp_start_button)
        zoom_layout.addStretch()  # 添加伸缩项，让按钮靠左排列
        zoom_layout.addWidget(self.rb_zoom_xy)
        zoom_layout.addWidget(self.rb_zoom_x)
        zoom_layout.addWidget(self.rb_zoom_y)

        zoom_layout.addWidget(self.help_button)

        zoom_groupbox.setLayout(zoom_layout)

        # 2. 中间的图表区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')  # 设置背景为白色
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        self.plot_widget.setLabel('left', '温度 (°C)')
        self.plot_widget.setLabel('bottom', '距离 (m)')
        self.plot_widget.setTitle('温度曲线', color='k', size='12pt')
        self.plot_widget.setYRange(10, 80)  # 设置一个默认的Y轴范围

        # 绘制示例曲线
        pen = pg.mkPen(color='b', width=2)
        self.temp_curve = self.plot_widget.plot(pen = pen)  #这里只写了pen所以报错了，因为第一个数据本该是x轴数据，所以类型错误，需要指定pen=pen

        # 3. 底部的日志表格
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels(["时间", "通道", "区域", "内容", "设定阈值", "实际温度"])
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.log_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选择
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列宽自适应

        # 添加示例日志数据
        self._add_sample_log_data()

        #将按钮的点击信号连接到槽函数
        self.temp_start_button.clicked.connect(self.temp_start_command)
        self.rb_zoom_xy.toggled.connect(self.on_zoom_mode_changed)
        self.rb_zoom_x.toggled.connect(self.on_zoom_mode_changed)
        self.rb_zoom_y.toggled.connect(self.on_zoom_mode_changed)
        self.help_button.clicked.connect(self.show_zoom_help_popup)

        # 将所有组件添加到右侧布局中
        layout.addWidget(zoom_groupbox)  # 先添加单选按钮组
        layout.addWidget(self.plot_widget, 4)  # 图表比例为4
        layout.addWidget(self.log_table, 1)  # 表格比例为1

        return right_widget

    @pyqtSlot()
    def temp_start_command(self):
        """
        发送接收温度数据的命令
        """
        command_string = "[E]>START#"
        self.network_manager.socket.write(command_string.encode('utf-8'))
        print("发送请求温度命令成功")

    @pyqtSlot(str)
    def update_status(self, message: str):
        """更新状态栏的文本，并记录到日志"""
        self.statusBar.showMessage(message)
        # 自动将所有状态消息添加到日志
        # if "已连接" in message or "错误" in message or "断开" in message:
        #     self.add_log_entry("状态", message)

    @pyqtSlot()
    def show_zoom_help_popup(self):
        """
        槽函数：创建一个并显示关于缩放模式的帮助信息弹窗。
        """
        # 使用 QMessageBox.information() 创建一个标准的信息提示框
        QMessageBox.information(
            self,  # 第一个参数是父窗口
            "缩放模式说明",  # 第二个参数是弹窗的标题
            # 第三个参数是弹窗要显示的主要内容
            "这里是对三种缩放模式的详细说明：\n\n"
            "• 自由缩放: 默认模式。鼠标滚轮可同时缩放X和Y轴，按住左键拖动可平移视图。\n\n"
            "• 仅X轴: 锁定Y轴。鼠标操作将只影响水平方向的缩放和平移。\n\n"
            "• 仅Y轴: 锁定X轴。鼠标操作将只影响垂直方向的缩放和平移。"
        )

    @pyqtSlot(bool)
    def on_zoom_mode_changed(self, checked):
        """
        一个槽函数处理所有缩放模式单选按钮的状态变化。
        """
        # 如果信号是由于“被取消选中”而发射的，我们直接忽略，只处理“被选中”的情况
        if not checked:
            return

        # 获取是哪个按钮发射了这个信号
        sender = self.sender()
        view_box = self.plot_widget.getViewBox()

        if sender == self.rb_zoom_xy:
            # 模式：XY缩放
            view_box.setMouseEnabled(x=True, y=True)
            view_box.enableAutoRange()  # 切换到自由模式时，自动恢复一次视图
            print("已切换到XY缩放模式")

        elif sender == self.rb_zoom_x:
            # 模式：仅X轴
            view_box.setMouseEnabled(x=True, y=False)
            print("已切换到仅X轴缩放模式")

        elif sender == self.rb_zoom_y:
            # 模式：仅Y轴
            view_box.setMouseEnabled(x=False, y=True)
            print("已切换到仅Y轴缩放模式")

    @pyqtSlot(dict)
    def update_temperature_display(self, data: dict):
        """
        核心槽函数：接收解析后的温度数据并更新图表。
        `data` 是从 DataParser 发射过来的包含所有信息的字典。
        """
        # a. 从字典中安全地取出温度数据（NumPy数组）
        temperatures = data.get("temperatures")
        if temperatures is None:
            return

        # b. 创建X轴数据（距离）
        num_points = len(temperatures)
        distances = np.arange(0, num_points * 0.5, 0.5)

        # c. 【关键】使用 setData() 高效更新曲线
        self.temp_curve.setData(distances, temperatures)

        # d. (可选) 更新一些摘要信息
        # max_temp = np.max(temperatures)
        # self.statusBar.showMessage(f"数据已更新 | 通道: {data.get('channel_id')} | 最高温度: {max_temp:.2f}°C")

    def _add_sample_log_data(self):
        """向表格中添加示例数据"""
        row_data = ["08-28 16:06:34", "通道1", "区域1", "报警: 预警", "设定阈值: 100.0c", "实际温度: ?"]
        row_position = self.log_table.rowCount()
        self.log_table.insertRow(row_position)
        for col, data in enumerate(row_data):
            self.log_table.setItem(row_position, col, QTableWidgetItem(data))
        # 插入一些空行
        for i in range(5):
            self.log_table.insertRow(self.log_table.rowCount())

    @pyqtSlot()
    def disconnect_device(self):
        """槽函数：响应“设备断开”菜单项"""
        print("正在断开连接...")
        self.network_manager.disconnect_from_host()

    def closeEvent(self, event):
        """重写窗口关闭事件，确保在关闭窗口时，后台线程也能被安全地停止。"""
        print("正在关闭应用程序...")
        self.network_manager.disconnect_from_host()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())