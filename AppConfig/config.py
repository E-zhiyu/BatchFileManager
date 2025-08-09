"""应用配置项模块"""

from qfluentwidgets import (qconfig, QConfig, ConfigItem, BoolValidator)


class Config(QConfig):
    """应用配置项"""
    tableColumnWidth = ConfigItem('FileTableView', 'ColumnWidth', None)  # 文件列表列宽
    customJavaPath = ConfigItem('Environment', 'CustomJavaPath', '')  # Java路径选项
    useCustomJavaPath = ConfigItem('Environment', 'UseCustomJavaPath', False, BoolValidator())


config_path = './config/app_config.json'
cfg = Config()
qconfig.load(config_path, cfg)
