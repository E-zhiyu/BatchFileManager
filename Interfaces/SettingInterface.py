"""设置界面模块"""
from PyQt6.QtWidgets import QWidget


class SettingInterface(QWidget):
    """设置界面类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingInterface")
