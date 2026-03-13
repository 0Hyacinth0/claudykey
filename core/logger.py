"""统一的日志系统模块。

提供全局日志配置和获取日志记录器的便捷方法。
"""
import logging
import sys
import os
from datetime import datetime
from typing import Optional


_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

_initialized = False


def setup_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_to_console: bool = True
) -> None:
    """初始化全局日志配置。
    
    Args:
        log_level: 日志级别，默认 INFO。
        log_file: 日志文件路径，如果为 None 则不写入文件。
        log_to_console: 是否输出到控制台。
    """
    global _initialized
    
    if _initialized:
        return
    
    handlers = []
    
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
        handlers.append(console_handler)
    
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=log_level,
        format=_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
        handlers=handlers
    )
    
    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器。
    
    Args:
        name: 日志记录器名称，通常使用 __name__。
        
    Returns:
        配置好的 Logger 实例。
    """
    if not _initialized:
        setup_logging()
    
    return logging.getLogger(name)


def get_default_log_file() -> str:
    """获取默认日志文件路径。
    
    Returns:
        默认日志文件路径。
    """
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(here, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join(log_dir, f'claudykey_{today}.log')
