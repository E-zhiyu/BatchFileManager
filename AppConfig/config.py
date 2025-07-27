"""应用配置项模块"""

from qfluentwidgets import (qconfig, QConfig, OptionsConfigItem, OptionsValidator, ConfigItem, BoolValidator)


class Config(QConfig):
    """应用配置项"""
    pass


config_path = './AppConfig'
cfg = Config()
qconfig.load(config_path, cfg)
