import struct

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import socket
import time

# 1.配置网络参数
MCU_IP = "192.168.100.123"  # MCU的IP地址
MCU_PORT = 5000             # MCU的通信端口
# 温度数据包大小固定是16023字节
TEMPERATURE_PACKET_SIZE = 16023

# 类1：数据解析
class DataParser(QObject):
    """
    一个专门用于解析DTS设备二进制通信协议的类。
    它接收原始字节数据，解析后通过信号发送出去。
    """
    # 定义信号，用于发送解析后的数据
    # 参数是解析后的数据结构，这里用dict或自定义类都可以，用dict更灵活
    temperature_data_ready = pyqtSignal(dict)
    # device_params_ready = pyqtSignal(dict)
    # alarm_data_ready = pyqtSignal(dict)

    # 其他数据类型的信号...

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buffer = b''  # 创建一个缓冲区来存储接收到的不完整数据，单位字节串(bytes)类型
        print("DataParser 初始化成功，缓冲区已创建。")

        # 这里可以实现创建文件夹功能

    def parse_data(self, raw_data):
        """
        这个方法接收来自NetworkThread的原始数据块。
        """
        # 1. 将新收到的数据追加到缓冲区的末尾
        self.buffer += raw_data

        # 持续循环，直到缓冲区中没有足够的数据构成一个完整的数据包
        while(self.buffer):
            # 一个数据包至少需要一个包头和长度信息
            if len(self.buffer) < 11:
                break  # 数据不够，等待下一次接收

            # --- 检查数据头 ---
            # 温度/Stokes/AntiStokes数据包
            if self.buffer.startswith(b'\xAA\x7B\x07\xAF\xEC\x66\x48\xC5'):
                # 根据协议，总数据长度在第9、10字节
                total_len_low = self.buffer[9]    #低位在前
                total_len_high = self.buffer[10]  #高位在后
                total_len = total_len_low + (total_len_high << 8)
                # 假设total_len是纯数据部分的长度，根据规律，温度数据长度恒为16023字节
                expected_packet_size = 22 + total_len    #此数据应恒为16023

                # 协议中对total_len的定义似乎是指纯数据长度，需要与实际设备确认
                # 我们先假设 total_len 是整个数据帧的长度（从第0位到结尾）
                expected_packet_size = total_len

                if len(self.buffer) >= expected_packet_size:
                    # 缓冲区数据足够，可以解析一个完整包
                    packet = self.buffer[:expected_packet_size]

                    # 检查结尾符
                    if packet.endswith(b'\x55'):
                        # 数据类型标志位在第11字节
                        data_type = packet[11]
                        if data_type == 0x00:  # 假设0x00代表温度数据
                            self._parse_temperature_packet(packet)
                        # else:
                        #     self._parse_stokes_packet(packet) 等...

                    # 从缓冲区移除已处理的数据包
                    self.buffer = self.buffer[expected_packet_size:]
                else:
                    # 数据包不完整，跳出循环等待更多数据
                    break

            # --- 检查设备参数数据头 ---
    #         elif self.buffer.startswith(b'\xA9\x7B\x07\xAF\xEC\x66\x48\xC5'):
    #             # 设备参数包是固定长度88字节
    #             if len(self.buffer) >= 88:
    #                 packet = self.buffer[:88]
    #                 if packet.endswith(b'\x55'):
    #                     self._parse_device_params_packet(packet)
    #                 self.buffer = self.buffer[88:]
    #             else:
    #                 break
    #
    #         # 其他数据包类型 (报警等) 在此添加 elif ...
    #
            else:
    #             # 如果缓冲区开头不是任何已知的数据头，说明数据同步出错
    #             # 寻找下一个可能的包头 b'\xAA' 或 b'\xA9'
                print("数据包头错误，正在尝试同步...")
                next_aa = self.buffer.find(b'\xAA', 1)
                next_a9 = self.buffer.find(b'\xA9', 1)

                # 找到最近的一个包头
    #             positions = [p for p in [next_aa, next_a9] if p != -1]
    #             if not positions:
    #                 # 没找到任何包头，清空缓冲区
    #                 self.buffer = b''
    #                 break
    #
    #             min_pos = min(positions)
    #             self.buffer = self.buffer[min_pos:]

    def _parse_temperature_packet(self, packet: bytes):
        """解析温度数据包"""
        print(f"温度数据包接收成功！接收到 {len(packet)}字节数据")
        # 已经接收到16023个字节，这是一个完整的温度数据包
        try:
            pass
            # 根据协议文档解析头部信息
            # '<' 表示小端序（低位在前高位在后）
            # 'B' 表示 unsigned char (1 byte)
            # 'H' 表示 unsigned short (2 bytes)
            header_format = '<8s B H B B H H H H B'
            header_size = struct.calcsize(header_format)  #计算这个结构占多少字节，固定是22字节

            header_data = struct.unpack(header_format, packet[:header_size]) # 通过切片操作，只取出头部对应的字节（22字节）
            # 将元组中的数据放到字典中
            parsed = {
                "device_id": header_data[1],        # 1个字节：设备ID
                "total_len": header_data[2],        # 2个字节：总数据长度
                "data_type": header_data[3],        # 1个字节：数据类型标志位（？0x00）
                                                    # 1个字节：保留位（跳过）
                "channel_id": header_data[5],       # 2个字节：通道标志位
                "data_start_point": header_data[6], # 2个字节：数据起点位置
                "data_end_point": header_data[7],   # 2个字节：数据终点位置
                "total_channels": header_data[8],   # 2个字节：总通道数量
                "current_channel": header_data[9]   # 1个字节：当前通道号（？？）
            }

            # 解析实际的温度数据
            # 每个温度点是 short int (2字节), 低位在前
            temp_data_bytes = packet[header_size:-1]  # -1 去掉结尾的0x55

            # '<' 小端序, 'h' 表示 signed short (2 bytes)
            num_points = len(temp_data_bytes) // 2      # 8000个温度点
            temp_format = f'<{num_points}h'

            # 解包的数据是元组，需要转成numpy数组
            raw_temps_tuple = struct.unpack(temp_format, temp_data_bytes)
            raw_temps_np = np.array(raw_temps_tuple)

            # 实际温度 = 解调值 / 100
            actual_temps = (raw_temps_np - 20000) / 100.0

            parsed["temperatures"] = actual_temps

            print(f"通道 {parsed['channel_id']} 收到 {len(actual_temps)} 个温度点")
            # print(actual_temps)
            # 发送信号
            self.temperature_data_ready.emit(parsed)

        except Exception as e:
            print(f"解析温度数据包失败: {e}")

    # def _parse_device_params_packet(self, packet: bytes):
    #     """解析设备参数包"""
    #     # 这个包是固定格式的，可以直接按位解析
    #     # 暂时只做示例，不全部解析
    #     try:
    #         device_id = packet[8]
    #         # 光纤盒温度 = (低位 + 高位 << 8)
    #         box_temp_raw = packet[13] + (packet[14] << 8)
    #
    #         params = {
    #             "device_id": device_id,
    #             "box_temperature": box_temp_raw / 100.0,  # 假设也需要除以100
    #             # ... 在这里根据协议文档添加其他所有参数的解析 ...
    #         }
    #         print(f"收到设备参数: {params}")
    #         self.device_params_ready.emit(params)
    #     except Exception as e:
    #         print(f"解析设备参数包失败: {e}")

# 二、网络通信线程：只负责TCP连接和接收原始字节流，然后传给DataParser
class NetworkThread(QThread):

    connection_status = pyqtSignal(str)

    def __init__(self, host, port, parser: DataParser, parent=None):
        super(NetworkThread, self).__init__(parent)
        self.host = host
        self.port = port
        self.parser = parser # 传入数据解析器实例
        self.running = True
        self._socket = None  # 现在没有连接

    # 线程里最核心的方法，当调用thread.start() 时，QThread 会自动在一个新的线程中执行这个 run 方法里的所有代码
    def run(self):
        print("进入 run 方法")

        while self.running:
            try:
                # self.connection_status.emit(f"正在连接到 {self.host}:{self.port}...")
                #创建一个TCP网络连接；指定使用IPv4地址族；指定使用TCP协议
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(5)
                print(f"正在尝试连接到 {MCU_IP}:{MCU_PORT} ...")
                self._socket.connect((self.host, self.port))
                print("---连接成功---")
                # self.connection_status.emit(f"已连接到 {self.host}:{self.port}")

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
                    # self.connection_status.emit("连接已断开，准备重连...")
                    self._socket.close()
                    time.sleep(5)

            except socket.timeout:
                # 如果连接超时
                print("❌ 错误：连接超时。")
                # self.connection_status.emit(f"连接失败: {e}")

            except ConnectionRefusedError:
                # 如果连接被MCU拒绝
                print("❌ 错误：连接被拒绝。")

            except Exception as e:
                # self.connection_status.emit(f"发生未知网络错误: {e}")
                print("❌ 错误：未知错误。")
                time.sleep(5)

    # 主窗口关闭时，调用此方法停止线程
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
    thread = NetworkThread(MCU_IP, MCU_PORT, parser)
    thread.run()