"""关于软件界面模块"""
from PyQt6.QtWidgets import QWidget


class InfoInterface(QWidget):
    """关于软件界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InfoInterface")
