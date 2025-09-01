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
from PyQt5.QtCore import QObject, pyqtSignal


class DataParser(QObject):
    """
    一个专门用于解析DTS设备二进制通信协议的类。
    它接收原始字节数据，解析后通过信号发送出去。
    """
    pass