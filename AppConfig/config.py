"""应用配置项模块"""

from qfluentwidgets import (qconfig, QConfig, OptionsConfigItem, OptionsValidator, ConfigItem, BoolValidator)


class Config(QConfig):
    """应用配置项"""
    tableColumnWidth = ConfigItem(  # 文件列表列宽
        'FileTableView', 'ColumnWidth', None
    )


config_path = './config/app_config.json'
cfg = Config()
qconfig.load(config_path, cfg)
