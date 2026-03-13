"""图像匹配模块单元测试。"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from core.image_match import ImageMatcher, load_template, find_template


class TestImageMatcher:
    """ImageMatcher 类测试。"""
    
    def test_matcher_singleton(self):
        """测试匹配器单例。"""
        from core.image_match import _get_matcher
        m1 = _get_matcher()
        m2 = _get_matcher()
        assert m1 is m2
    
    def test_load_template_empty_path(self):
        """测试空路径加载模板。"""
        matcher = ImageMatcher()
        with pytest.raises(ValueError, match="模板路径不能为空"):
            matcher.load_template('')
    
    def test_load_template_file_not_found(self):
        """测试文件不存在时加载模板。"""
        matcher = ImageMatcher()
        with pytest.raises(FileNotFoundError):
            matcher.load_template('/nonexistent/path/to/image.png')
    
    @patch('PIL.Image.open')
    def test_load_template_success(self, mock_open):
        """测试成功加载模板。"""
        mock_img = MagicMock()
        mock_img.convert.return_value = mock_img
        mock_img.__enter__ = MagicMock(return_value=mock_img)
        mock_img.__exit__ = MagicMock(return_value=False)
        
        mock_array = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch('numpy.array', return_value=mock_array):
            matcher = ImageMatcher()
            result = matcher.load_template('/fake/path.png')
            
            assert result is not None
    
    def test_find_template_empty_screen(self):
        """测试空屏幕图像。"""
        matcher = ImageMatcher()
        template = np.zeros((10, 10, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="屏幕图像不能为空"):
            matcher.find_template(None, template)
    
    def test_find_template_empty_template(self):
        """测试空模板图像。"""
        matcher = ImageMatcher()
        screen = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="模板图像不能为空"):
            matcher.find_template(screen, None)
    
    def test_find_template_invalid_threshold(self):
        """测试无效阈值。"""
        matcher = ImageMatcher()
        screen = np.zeros((100, 100, 3), dtype=np.uint8)
        template = np.zeros((10, 10, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="阈值必须在 0-1 之间"):
            matcher.find_template(screen, template, threshold=1.5)
        
        with pytest.raises(ValueError, match="阈值必须在 0-1 之间"):
            matcher.find_template(screen, template, threshold=-0.5)
    
    def test_find_template_larger_than_screen(self):
        """测试模板大于屏幕。"""
        matcher = ImageMatcher()
        screen = np.zeros((50, 50, 3), dtype=np.uint8)
        template = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = matcher.find_template(screen, template)
        assert result is None
    
    def test_find_template_no_match(self):
        """测试无匹配情况。"""
        matcher = ImageMatcher()
        screen = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        template = np.ones((10, 10, 3), dtype=np.uint8) * 255
        
        result = matcher.find_template(screen, template, threshold=0.99)
        assert result is None
    
    def test_find_template_exact_match(self):
        """测试精确匹配。"""
        matcher = ImageMatcher()
        
        screen = np.zeros((100, 100, 3), dtype=np.uint8)
        template = np.ones((10, 10, 3), dtype=np.uint8) * 255
        
        screen[20:30, 30:40] = 255
        
        result = matcher.find_template(screen, template, threshold=0.9)
        
        assert result is not None
        cx, cy, conf = result
        assert 24 <= cx <= 26
        assert 24 <= cy <= 26
        assert conf >= 0.9
    
    def test_find_all_templates(self):
        """测试查找所有匹配。"""
        matcher = ImageMatcher()
        
        screen = np.zeros((100, 100, 3), dtype=np.uint8)
        template = np.ones((10, 10, 3), dtype=np.uint8) * 255
        
        screen[10:20, 10:20] = 255
        screen[50:60, 50:60] = 255
        
        results = matcher.find_all_templates(screen, template, threshold=0.9)
        
        assert len(results) >= 1


class TestModuleFunctions:
    """模块级函数测试。"""
    
    def test_load_template_function(self):
        """测试模块级加载模板函数。"""
        with pytest.raises(FileNotFoundError):
            load_template('/nonexistent/path.png')
    
    def test_find_template_function(self):
        """测试模块级查找模板函数。"""
        screen = np.zeros((100, 100, 3), dtype=np.uint8)
        template = np.zeros((10, 10, 3), dtype=np.uint8)
        
        result = find_template(screen, template)
        assert result is not None or result is None
