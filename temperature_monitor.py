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
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from dataParser import DataParser

# 网络通信线程
class NetworkThread(QThread):
    def __init__(self, host, port, parser: DataParser, parent=None):
        # super(NetworkThread, self).__init__(parent)
        self.host = host
        self.port = port
        self.running = True
