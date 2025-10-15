# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: temperature_monitor.py
@Author: 杜塞米
@CreateDate: 2025/9/1
@LastEditTime: 
@Description: 
@Version: 1.0
"""
from PyQt5.QtCore import QThread, pyqtSignal
from dataParser import DataParser
import socket
import time

# 网络通信线程：只负责TCP连接和接收原始字节流，然后传给DataParser
class NetworkThread(QThread):
    #子线程不能直接操作GUI，需要通过信号和主线程连接
    connection_status = pyqtSignal(str)

    def __init__(self, host, port, parser: DataParser, parent=None):
        super(NetworkThread, self).__init__(parent)
        self.host = host
        self.port = port
        self.running = True
        self.parser = parser
        self._socket = None  # 现在没有连接

    # 线程里最核心的方法，当调用thread.start() 时，QThread 会自动在一个新的线程中执行这个 run 方法里的所有代码
    def run(self):
        while self.running:
            try:
                self.connection_status.emit(f"正在连接到 {self.host}:{self.port}...")
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(5)
                self._socket.connect((self.host, self.port))
                self.connection_status.emit(f"已连接到 {self.host}:{self.port}")

                while self.running:
                    # 接收数据，缓冲区大小可以根据实际情况调整
                    data = self._socket.recv(4096)
                    if not data:
                        # 连接被对方关闭
                        break

                    # 将收到的原始数据交给解析器处理
                    self.parser.parse_data(data)

                if self.running:
                    # 如果是正常循环退出（对方关闭），则触发断线重连
                    self.connection_status.emit("连接已断开，准备重连...")
                    self._socket.close()
                    time.sleep(5)

            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                self.connection_status.emit(f"连接失败: {e}")
                time.sleep(5)
            except Exception as e:
                self.connection_status.emit(f"发生未知网络错误: {e}")
                time.sleep(5)

    #主窗口关闭时，调用此方法停止线程
    def stop(self):
            self.running = False
            if self._socket:
                try:
                    # 关闭socket以中断阻塞的recv调用
                    self._socket.shutdown(socket.SHUT_RDWR)
                    self._socket.close()
                except OSError:
                    pass
            self.quit()
            self.wait()

    def send_command(self, command: str):
            """发送文本命令到设备"""
            if self._socket and self.running:
                try:
                    # 命令需要编码为字节串发送
                    self._socket.sendall(command.encode('utf-8'))
                    print(f"已发送命令: {command}")
                except OSError as e:
                    self.connection_status.emit(f"命令发送失败: {e}")



# # --- 程序从这里开始运行 ---
if __name__ == "__main__":
    parser = DataParser()
    net = NetworkThread()