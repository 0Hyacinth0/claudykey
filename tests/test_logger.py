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
    
    def test_setup_logging_with_file(self):
        """测试带文件的日志设置。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            setup_logging(
                log_level=logging.DEBUG,
                log_file=log_file,
                log_to_console=False
            )
            
            logger = get_logger('test_file')
            logger.info("测试日志消息")
            
            assert os.path.exists(log_file)
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '测试日志消息' in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
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
    
    def test_log_levels(self):
        """测试不同日志级别。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            setup_logging(
                log_level=logging.DEBUG,
                log_file=log_file,
                log_to_console=False
            )
            
            logger = get_logger('test_levels')
            
            logger.debug("Debug 消息")
            logger.info("Info 消息")
            logger.warning("Warning 消息")
            logger.error("Error 消息")
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'Debug 消息' in content
                assert 'Info 消息' in content
                assert 'Warning 消息' in content
                assert 'Error 消息' in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_log_format(self):
        """测试日志格式。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            setup_logging(
                log_level=logging.INFO,
                log_file=log_file,
                log_to_console=False
            )
            
            logger = get_logger('test_format')
            logger.info("格式测试")
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert ' - ' in content
                assert 'test_format' in content
                assert 'INFO' in content
                assert '格式测试' in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_setup_logging_idempotent(self):
        """测试重复调用 setup_logging 不会重复初始化。"""
        setup_logging(log_to_console=False)
        first_initialized = _initialized
        
        setup_logging(log_to_console=False)
        second_initialized = _initialized
        
        assert first_initialized is True
        assert second_initialized is True
    
    def test_logger_with_exception(self):
        """测试异常日志记录。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            setup_logging(
                log_level=logging.DEBUG,
                log_file=log_file,
                log_to_console=False
            )
            
            logger = get_logger('test_exception')
            
            try:
                raise ValueError("测试异常")
            except ValueError as e:
                logger.exception("捕获异常")
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '捕获异常' in content
                assert 'ValueError' in content
                assert '测试异常' in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
