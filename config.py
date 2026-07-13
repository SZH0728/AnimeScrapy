# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 全局配置模块
@details 读取 INI 配置文件，以模块级单例 config 暴露全部配置项。
         INI 文件路径优先从环境变量 ANIME_SCRAPY_CONFIG 读取，
         未设置时降级为进程工作目录下的 config.ini（适配本地开发与 Docker 挂载）。
         setup_logging() 从 [logging] 节读取参数，根据 [app] debug 开关
         选择开发模式（控制台）或生产模式（文件轮转），由 main.py 唯一调用一次。
         本模块不导入任何项目内部模块，可被任意层级安全导入。
"""

from os import environ
from configparser import RawConfigParser, SectionProxy
from logging import DEBUG, ERROR, Formatter, INFO, StreamHandler, WARNING, getLogger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

_CONFIG_PATH: str = environ.get('ANIME_SCRAPY_CONFIG', 'config.ini')

config: RawConfigParser = RawConfigParser()
config.read(_CONFIG_PATH, encoding='utf-8')


def setup_logging() -> None:
    """
    @brief 初始化日志配置
    @details 根据 [app] debug 配置项自动切换策略：
             debug = true  → 开发模式（控制台 StreamHandler，DEBUG 级别，短时间戳）
             debug = false → 生产模式（双文件 TimedRotatingFileHandler，INFO/ERROR 分离）
             两种模式均压制 suppress_libs 中各库的 DEBUG 噪音。
             全部参数从 config [logging] 节读取，不接受外部入参。
    @throws KeyError 当 config.ini 缺失必要配置键时
    """
    is_debug: bool = config.getboolean('app', 'debug')

    log_config: SectionProxy = config['logging']
    log_format: str = log_config['format']
    log_dir: str = log_config['log_dir']

    info_backup: int = config.getint('logging', 'info_backup_count')
    error_backup: int = config.getint('logging', 'error_backup_count')
    suppress_libs: list[str] = [lib.strip() for lib in log_config['suppress_libs'].split(',')]

    root = getLogger()
    root.setLevel(DEBUG)

    if is_debug:
        handler = StreamHandler()
        handler.setLevel(DEBUG)
        handler.setFormatter(Formatter(log_format, datefmt=log_config['date_format_debug']))
        root.addHandler(handler)
    else:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        formatter = Formatter(log_format, datefmt=log_config['date_format_prod'])

        info_h = TimedRotatingFileHandler(f'{log_dir}/info.log', when='midnight', backupCount=info_backup, encoding='utf-8',)
        info_h.setLevel(INFO)
        info_h.setFormatter(formatter)

        error_h = TimedRotatingFileHandler(f'{log_dir}/error.log', when='midnight', backupCount=error_backup, encoding='utf-8',)
        error_h.setLevel(ERROR)
        error_h.setFormatter(formatter)

        root.addHandler(info_h)
        root.addHandler(error_h)

    for lib in suppress_libs:
        getLogger(lib).setLevel(WARNING)


if __name__ == '__main__':
    pass
