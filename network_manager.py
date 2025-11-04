# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: network_manager.py
@Author: 杜塞米
@CreateDate: 2025/10/31
@LastEditTime: 
@Description: 
@Version: 1.0
"""
# -----------------------------------------------------------------------------
# 描述:
#   使用 PyQt5 的 QTcpSocket 来管理异步网络连接。
#   这个类取代了之前基于 'socket' 和 'QThread' 的 NetworkThread。
#   它被设计为在主线程中运行，并利用 Qt 的事件循环和信号槽机制。
# -----------------------------------------------------------------------------
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket
from old_folder.network_thread import DataParser
# QTcpSocket 是一个专门为 TCP 通信设计好的、功能完整的类（Class）

MCU_IP = "192.168.100.123"  # MCU的IP地址
MCU_PORT = 5000             # MCU的通信端口

class NetworkManager(QObject):
    """
    使用 QTcpSocket (非阻塞, 事件驱动) 来管理网络连接。
    """

    # 信号1: 用于在UI上显示连接状态 (与 NetworkThread 保持一致)
    connection_status = pyqtSignal(str)

    def __init__(self, parser: DataParser, parent=None):
        """
        初始化网络管理器。
        - parser: 传入 DataParser 实例，用于处理收到的数据。
        """
        super().__init__(parent)

        self.socket = QTcpSocket(self)   # 内部的构造函数已经完成了连接MCU的底层设置
        self.parser = parser

        self.host = MCU_IP
        self.port = MCU_PORT

        # --- 核心: 连接 QTcpSocket 的内置信号到我们的槽函数 ---

        # 1. 当连接成功时触发
        self.socket.connected.connect(self.on_connected)

        # 2. 当连接断开时触发
        self.socket.disconnected.connect(self.on_disconnected)

        # 3. 当有新数据到达网络缓冲区时触发
        #    这取代了 'while True: socket.recv()' 循环
        self.socket.readyRead.connect(self.on_ready_read)

        # 4. 当发生错误时触发
        #    注意: 旧的 .error() 信号已弃用，使用 .errorOccurred()
        self.socket.errorOccurred.connect(self.on_error)

    # --- QTcpSocket 的槽函数 ---

    @pyqtSlot()
    def on_connected(self):
        """当套接字成功连接时由 .connected 信号触发"""
        status_msg = f"✅ 已连接到 {self.host}:{self.port}"
        self.connection_status.emit(status_msg)
        print(status_msg)

    @pyqtSlot()
    def on_disconnected(self):
        """当套接字断开连接时由 .disconnected 信号触发"""
        status_msg = "🔌 连接已断开。"
        self.connection_status.emit(status_msg)
        print(status_msg)

    @pyqtSlot()
    def on_ready_read(self):
        """
        当网络缓冲区有新数据到达时，由 .readyRead 信号触发。
        """
        # .readAll() 读取缓冲区中 *所有* 可用的数据
        raw_data = self.socket.readAll()

        # 将 QByteArray 转换为 Python bytes，以便 DataParser 处理
        data_bytes = bytes(raw_data)

        # 将数据片段喂给 DataParser (DataParser 的逻辑完全不变)
        if self.parser:
            self.parser.parse_data(data_bytes)

    @pyqtSlot(QAbstractSocket.SocketError)
    def on_error(self, socket_error):
        """当发生套接字错误时由 .errorOccurred 信号触发"""
        error_message = self.socket.errorString()
        status_msg = f"❌ 网络错误: {error_message}"
        self.connection_status.emit(status_msg)
        print(f"{status_msg} (代码: {socket_error})")

    # --- 公共控制方法 (由 MainWindow 调用) ---

    @pyqtSlot(str, int)
    def connect_to_host(self, host: str, port: int):
        """
        由 MainWindow 调用以发起连接。
        这是一个非阻塞调用，它会立即返回，连接结果将通过信号通知。
        """
        self.host = host
        self.port = port

        status_msg = f"正在连接到 {host}:{port}..."
        self.connection_status.emit(status_msg)
        print(status_msg)

        # 如果之前有连接，先断开
        if self.socket.state() != QAbstractSocket.UnconnectedState:
            self.socket.abort()

        self.socket.connectToHost(host, port)    #非阻塞调用，不会像 socket.connect() 那样卡住程序

    @pyqtSlot()
    def disconnect_from_host(self):
        """由 MainWindow 调用以主动断开连接。"""
        if self.socket.state() == QAbstractSocket.ConnectedState:
            self.socket.disconnectFromHost()
        elif self.socket.state() == QAbstractSocket.ConnectingState:
            self.socket.abort()  # 如果正在连接中，则中止
        print("断开连接指令已发出。")

    @pyqtSlot(str)
    def send_command(self, command_str: str):
        """
        发送一个字符串命令。
        """
        if self.socket.state() == QAbstractSocket.ConnectedState:
            try:
                command_bytes = command_str.encode('utf-8')
                self.socket.write(command_bytes)
                self.socket.flush()  # 确保数据立即发送
                print(f"已发送命令: {command_str}")
            except Exception as e:
                status_msg = f"❌ 命令 '{command_str}' 发送失败: {e}"
                self.connection_status.emit(status_msg)
                print(status_msg)
        else:
            status_msg = "❌ 发送失败: 未连接"
            self.connection_status.emit(status_msg)
            print(status_msg)
