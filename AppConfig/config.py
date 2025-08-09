"""应用配置项模块"""

from qfluentwidgets import (qconfig, QConfig, ConfigItem)


class Config(QConfig):
    """应用配置项"""
    tableColumnWidth = ConfigItem('FileTableView', 'ColumnWidth', None)  # 文件列表列宽
    javaPath = ConfigItem('Environment', 'JavaPath', None)  # Java路径选项


config_path = './config/app_config.json'
cfg = Config()
qconfig.load(config_path, cfg)
