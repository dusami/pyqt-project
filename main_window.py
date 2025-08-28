import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QListWidget, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QHeaderView, QMenuBar, QAction, QStatusBar
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("分布式光纤温度监测系统 测试版1.0")
        self.setGeometry(100, 100, 1600, 900)  # 设置一个较大的默认窗口尺寸

        # --- 创建菜单栏和状态栏 ---
        self._create_menu_bar()
        self._create_status_bar()

        # --- 主窗口中心布局 ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 使用水平布局，将窗口分为左右两部分
        main_layout = QHBoxLayout(main_widget)

        # --- 创建左侧面板 ---
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)

        # --- 创建右侧面板 ---
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 5)  # 让右侧面板占据更多空间 (比例为5:1)

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

        # --- 2. 创建其他顶层菜单 ---
        menus = ["显示设置", "权限管理", "设备配置", "运行记录", "报警分区及转发", "技术支持"]
        for menu_name in menus:
            menu_bar.addMenu(menu_name)

    def connect_device(self):
        pass
    def disconnect_device(self):
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

        # 1. 通道列表
        channel_group = QGroupBox("当前DTS主机:[Next1]")
        channel_layout = QVBoxLayout()
        self.channel_list = QListWidget()
        for i in range(1, 8):
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
        """创建并返回右侧面板的QWidget"""
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)

        # 1. 图表上方的控制栏 (简化版)
        plot_control_layout = QHBoxLayout()
        plot_control_layout.addWidget(QLabel("通道: 通道1 [16:11:22]"))
        plot_control_layout.addStretch()  # 添加伸缩项，将按钮推到右边
        plot_control_layout.addWidget(QPushButton("功能按钮"))
        plot_control_layout.addWidget(QPushButton("历史查询"))
        plot_control_layout.addWidget(QPushButton("实时曲线"))

        # 2. 中间的图表区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')  # 设置背景为白色
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        self.plot_widget.setLabel('left', '温度 (°C)')
        self.plot_widget.setLabel('bottom', '距离 (m)')
        self.plot_widget.setTitle('温度曲线', color='k', size='12pt')

        # 绘制示例曲线
        self._plot_sample_data()

        # 3. 底部的日志表格
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels(["时间", "通道", "区域", "内容", "设定阈值", "实际温度"])
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.log_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选择
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列宽自适应

        # 添加示例日志数据
        self._add_sample_log_data()

        # 将所有组件添加到右侧布局中
        layout.addLayout(plot_control_layout)
        layout.addWidget(self.plot_widget, 4)  # 图表比例为4
        layout.addWidget(self.log_table, 1)  # 表格比例为1

        return right_widget

    def _plot_sample_data(self):
        """生成并绘制与截图中类似的示例数据"""
        # 生成 x 轴数据 (距离)
        x = np.arange(0, 1200, 1)
        # 生成 y 轴数据 (温度)
        y = np.full_like(x, 37.5, dtype=float)
        # 添加一些随机噪声
        y += np.random.normal(0, 0.3, len(x))
        # 在1000m处创建一个阶跃下降
        y[1000:] -= 15
        y[1000:] += np.random.normal(0, 0.2, len(y[1000:]))

        pen = pg.mkPen(color=(0, 0, 200), width=2)  # 蓝色画笔
        self.plot_widget.plot(x, y, pen=pen)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())