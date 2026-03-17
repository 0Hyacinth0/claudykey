"""日志系统单元测试。"""
import pytest
import logging
import tempfile
import os
from unittest.mock import patch

from core.logger import (
    setup_logging,
    get_logger,
    get_default_log_file,
    _initialized
)


class TestLogger:
    """日志系统测试。"""
    
    def setup_method(self):
        """每个测试方法前重置日志系统状态。"""
        import core.logger
        core.logger._initialized = False
        
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    def test_setup_logging_basic(self):
        """测试基本日志设置。"""
        setup_logging(log_to_console=False)
        
        logger = get_logger('test')
        assert logger is not None
        assert isinstance(logger, logging.Logger)
    
    def test_get_logger_returns_same_instance(self):
        """测试获取相同名称的 logger 返回同一实例。"""
        setup_logging(log_to_console=False)
        
        logger1 = get_logger('same_name')
        logger2 = get_logger('same_name')
        
        assert logger1 is logger2
    
    def test_get_logger_different_names(self):
        """测试不同名称返回不同 logger。"""
        setup_logging(log_to_console=False)
        
        logger1 = get_logger('name1')
        logger2 = get_logger('name2')
        
        assert logger1 is not logger2
    
    def test_get_default_log_file(self):
        """测试获取默认日志文件路径。"""
        log_path = get_default_log_file()
        
        assert log_path is not None
        assert log_path.endswith('.log')
        assert 'claudykey' in log_path
    
    def test_setup_logging_idempotent(self):
        """测试重复调用 setup_logging 不会重复初始化。"""
        setup_logging(log_to_console=False)
        first_initialized = _initialized
        
        setup_logging(log_to_console=False)
        second_initialized = _initialized
        
        assert first_initialized is True
        assert second_initialized is True
    
    def test_logger_has_handlers(self):
        """测试 logger 有处理器。"""
        setup_logging(log_to_console=True)
        
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0
    
    def test_logger_level(self):
        """测试日志级别设置。"""
        setup_logging(log_level=logging.DEBUG, log_to_console=False)
        
        logger = get_logger('test_level')
        assert logger.level <= logging.DEBUG or logging.getLogger().level <= logging.DEBUG
    
    def test_default_log_file_creates_directory(self):
        """测试默认日志文件创建目录。"""
        log_path = get_default_log_file()
        log_dir = os.path.dirname(log_path)
        
        assert os.path.exists(log_dir)
