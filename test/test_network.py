# -*- coding: utf-8 -*-
"""
@Project: pyqt-project
@File: test_network.py
@Author: 杜塞米
@CreateDate: 2025/9/1
@LastEditTime: 
@Description: 
@Version: 1.0
"""

import socket
import time

# 1.配置网络参数
MCU_IP = "192.168.100.123"  # MCU的IP地址
MCU_PORT = 5000             # MCU的通信端口

def connect_and_receive():
    # IPv4, TCP协议
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #设置超时
    client_socket.settimeout(10)

    try:
        print(f"正在尝试连接到 {MCU_IP}:{MCU_PORT} ...")
        client_socket.connect((MCU_IP, MCU_PORT))
        print("---连接成功---")

        #接收数据
        print("--- 等待接收MCU数据 ---")
        while True:
            # 尝试从MCU接收最多4096字节的数据
            # .recv() 会在这里暂停，直到收到数据或超时
            data = client_socket.recv(4096)

            if not data:
                # 如果data是空的，说明MCU主动断开了连接
                print("🔌 MCU断开了连接。")
                break

            # 打印收到的数据信息
            # 我们将收到的原始二进制数据转换成十六进制字符串打印出来，方便你和协议文档对比
            # 生成器表达式；{byte:02X}：格式化说明符；至少两位数字，不足时前面补0
            # {byte:02X}：格式说明符；X 表示十六进制（大写字母 A-F）；02 表示宽度为 2，不足两位前面补 0。
            hex_data = ' '.join(f'0x{byte:02X}' for byte in data)

            print(f"接收到 {len(data)} 字节数据: {hex_data}")

    except socket.timeout:
        # 如果连接超时
        print("❌ 错误：连接超时。")

    except ConnectionRefusedError:
        # 如果连接被MCU拒绝
        print("❌ 错误：连接被拒绝。")

    except Exception as e:
        # 捕获其他可能的异常
        print(f"❌ 发生未知错误: {e}")

    finally:
        # 无论成功还是失败，最后都要关闭socket连接
        print("--- 关闭连接 ---")
        client_socket.close()

# --- 程序从这里开始运行 ---
if __name__ == "__main__":
    connect_and_receive()