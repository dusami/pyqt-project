# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: dataParser.py
@Author: 杜塞米
@CreateDate: 2025/9/1
@LastEditTime: 
@Description: 
@Version: 1.0
"""
# 放到代码文件的开头部分
import struct
from PyQt5.QtCore import QObject, pyqtSignal


class DataParser(QObject):
    """
    一个专门用于解析DTS设备二进制通信协议的类。
    它接收原始字节数据，解析后通过信号发送出去。
    """
    # 定义信号，用于发送解析后的数据
    # 参数是解析后的数据结构，这里用dict或自定义类都可以，用dict更灵活
    temperature_data_ready = pyqtSignal(dict)
    device_params_ready = pyqtSignal(dict)
    alarm_data_ready = pyqtSignal(dict)

    # 其他数据类型的信号...

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buffer = b''  # 创建一个缓冲区来存储接收到的不完整数据

    def parse_data(self, raw_data: bytes):
        """
        接收原始字节流，并尝试解析数据包。
        """
        # 将新接收到的数据追加到缓冲区
        self.buffer += raw_data

        # 持续循环，直到缓冲区中没有足够的数据构成一个完整的数据包
        while True:
            # 一个数据包至少需要一个包头和长度信息
            if len(self.buffer) < 11:
                break  # 数据不够，等待下一次接收

            # --- 检查数据头 ---
            # 温度/Stokes/AntiStokes数据包
            if self.buffer.startswith(b'\xAA\x7B\x07\xAF\xEC\x66\x48\xC5'):
                # 根据协议，总数据长度在第9、10字节
                total_len_low = self.buffer[9]
                total_len_high = self.buffer[10]
                total_len = total_len_low + (total_len_high << 8)

                expected_packet_size = 22 + total_len  # 假设total_len是纯数据部分的长度

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
            elif self.buffer.startswith(b'\xA9\x7B\x07\xAF\xEC\x66\x48\xC5'):
                # 设备参数包是固定长度88字节
                if len(self.buffer) >= 88:
                    packet = self.buffer[:88]
                    if packet.endswith(b'\x55'):
                        self._parse_device_params_packet(packet)
                    self.buffer = self.buffer[88:]
                else:
                    break

            # 其他数据包类型 (报警等) 在此添加 elif ...

            else:
                # 如果缓冲区开头不是任何已知的数据头，说明数据同步出错
                # 寻找下一个可能的包头 b'\xAA' 或 b'\xA9'
                print("数据包头错误，正在尝试同步...")
                next_aa = self.buffer.find(b'\xAA', 1)
                next_a9 = self.buffer.find(b'\xA9', 1)

                # 找到最近的一个包头
                positions = [p for p in [next_aa, next_a9] if p != -1]
                if not positions:
                    # 没找到任何包头，清空缓冲区
                    self.buffer = b''
                    break

                min_pos = min(positions)
                self.buffer = self.buffer[min_pos:]

    def _parse_temperature_packet(self, packet: bytes):
        """解析温度数据包"""
        try:
            # 根据协议文档解析头部信息
            # '<' 表示小端序
            # 'B' 表示 unsigned char (1 byte)
            # 'H' 表示 unsigned short (2 bytes)
            header_format = '<8s B H B B H H H H H B'
            header_size = struct.calcsize(header_format)

            header_data = struct.unpack(header_format, packet[:header_size])

            parsed = {
                "device_id": header_data[1],
                "total_len": header_data[2],
                "data_type": header_data[3],
                "channel_id": header_data[5],
                "data_start_point": header_data[6],
                "data_end_point": header_data[7],
                "total_channels": header_data[8],
                "current_channel": header_data[9]
            }

            # 解析实际的温度数据
            # 每个温度点是 short int (2字节), 低位在前
            temp_data_bytes = packet[header_size:-1]  # -1 去掉结尾的0x55

            # '<' 小端序, 'h' 表示 signed short (2 bytes)
            num_points = len(temp_data_bytes) // 2
            temp_format = f'<{num_points}h'

            raw_temps = struct.unpack(temp_format, temp_data_bytes)

            # 实际温度 = 解调值 / 100
            actual_temps = [t / 100.0 for t in raw_temps]

            parsed["temperatures"] = actual_temps

            print(f"通道 {parsed['channel_id']} 收到 {len(actual_temps)} 个温度点")

            # 发送信号
            self.temperature_data_ready.emit(parsed)

        except Exception as e:
            print(f"解析温度数据包失败: {e}")

    def _parse_device_params_packet(self, packet: bytes):
        """解析设备参数包"""
        # 这个包是固定格式的，可以直接按位解析
        # 暂时只做示例，不全部解析
        try:
            device_id = packet[8]
            # 光纤盒温度 = (低位 + 高位 << 8)
            box_temp_raw = packet[13] + (packet[14] << 8)

            params = {
                "device_id": device_id,
                "box_temperature": box_temp_raw / 100.0,  # 假设也需要除以100
                # ... 在这里根据协议文档添加其他所有参数的解析 ...
            }
            print(f"收到设备参数: {params}")
            self.device_params_ready.emit(params)
        except Exception as e:
            print(f"解析设备参数包失败: {e}")