"""应用配置项模块"""
from PyQt6.QtCore import pyqtSignal

from qfluentwidgets import (qconfig, QConfig, ConfigItem, BoolValidator)


class Config(QConfig):
    """应用配置项和配置信号"""

    #配置信号
    fileDataChanged = pyqtSignal()
    presetDataChanged = pyqtSignal()

    # 配置项
    tableColumnWidth = ConfigItem('FileTableView', 'ColumnWidth', None)  # 文件列表列宽
    customJavaPath = ConfigItem('Environment', 'CustomJavaPath', '')  # Java路径选项
    useCustomJavaPath = ConfigItem('Environment', 'UseCustomJavaPath', False, BoolValidator())

    appVersion = ConfigItem('AppVersion', 'Version', '')  # 保存应用版本号


config_path = './config/app_config.json'
cfg = Config()
qconfig.load(config_path, cfg)
