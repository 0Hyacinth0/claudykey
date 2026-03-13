"""Screen capture using mss (fast, cross-platform).

提供屏幕截图功能，使用 mss 库实现高性能截图。
"""
import mss
import numpy as np
from typing import Tuple, Optional

from .logger import get_logger

logger = get_logger(__name__)


class ScreenCapture:
    """屏幕截图单例类。
    
    使用单例模式管理 mss 实例，避免重复创建。
    """
    
    _instance: Optional['ScreenCapture'] = None
    _sct: Optional[mss.base.MSSBase] = None
    
    def __new__(cls) -> 'ScreenCapture':
        """确保单例实例唯一性。"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _initialize_sct(self) -> None:
        """初始化 mss 截图实例。
        
        Raises:
            RuntimeError: mss 初始化失败。
        """
        if self._sct is not None:
            return
        
        try:
            logger.debug("初始化 mss 截图实例...")
            self._sct = mss.mss()
            logger.debug("mss 截图实例初始化完成")
        except Exception as e:
            logger.error(f"mss 初始化失败: {e}")
            raise RuntimeError(f"屏幕截图初始化失败: {e}") from e
    
    @property
    def sct(self) -> mss.base.MSSBase:
        """获取 mss 截图实例。
        
        Returns:
            mss MSSBase 实例。
        """
        if self._sct is None:
            self._initialize_sct()
        return self._sct
    
    def capture_region(self, x: int, y: int, w: int, h: int) -> np.ndarray:
        """捕获指定屏幕区域。
        
        Args:
            x: 区域左上角 X 坐标。
            y: 区域左上角 Y 坐标。
            w: 区域宽度。
            h: 区域高度。
            
        Returns:
            BGR 格式的 numpy 数组。
            
        Raises:
            ValueError: 区域参数无效。
            RuntimeError: 截图失败。
        """
        if w <= 0 or h <= 0:
            raise ValueError(f"区域尺寸无效: width={w}, height={h}")
        
        try:
            monitor = {'left': x, 'top': y, 'width': w, 'height': h}
            screenshot = self.sct.grab(monitor)
            result = np.array(screenshot)[:, :, :3]
            logger.debug(f"截图成功: ({x}, {y}) {w}x{h}")
            return result
        except mss.ScreenShotError as e:
            logger.error(f"截图失败: {e}")
            raise RuntimeError(f"屏幕截图失败: {e}") from e
        except Exception as e:
            logger.error(f"截图处理失败: {e}")
            raise RuntimeError(f"截图处理失败: {e}") from e
    
    def capture_fullscreen(self) -> np.ndarray:
        """捕获主显示器全屏。
        
        Returns:
            BGR 格式的 numpy 数组。
            
        Raises:
            RuntimeError: 截图失败。
        """
        try:
            monitor = self.sct.monitors[1]
            screenshot = self.sct.grab(monitor)
            result = np.array(screenshot)[:, :, :3]
            logger.debug(f"全屏截图成功: {monitor['width']}x{monitor['height']}")
            return result
        except IndexError:
            logger.error("未找到主显示器")
            raise RuntimeError("未找到主显示器") from None
        except Exception as e:
            logger.error(f"全屏截图失败: {e}")
            raise RuntimeError(f"全屏截图失败: {e}") from e
    
    def get_screen_size(self) -> Tuple[int, int]:
        """获取主显示器尺寸。
        
        Returns:
            (宽度, 高度) 元组。
            
        Raises:
            RuntimeError: 获取尺寸失败。
        """
        try:
            m = self.sct.monitors[1]
            return m['width'], m['height']
        except IndexError:
            logger.error("未找到主显示器")
            raise RuntimeError("未找到主显示器") from None
        except Exception as e:
            logger.error(f"获取屏幕尺寸失败: {e}")
            raise RuntimeError(f"获取屏幕尺寸失败: {e}") from e


_capture: Optional[ScreenCapture] = None


def _get_capture() -> ScreenCapture:
    """获取屏幕截图单例实例。
    
    Returns:
        ScreenCapture 实例。
    """
    global _capture
    if _capture is None:
        _capture = ScreenCapture()
    return _capture


def capture_region(x: int, y: int, w: int, h: int) -> np.ndarray:
    """捕获指定屏幕区域。
    
    Args:
        x: 区域左上角 X 坐标。
        y: 区域左上角 Y 坐标。
        w: 区域宽度。
        h: 区域高度。
        
    Returns:
        BGR 格式的 numpy 数组。
    """
    return _get_capture().capture_region(x, y, w, h)


def capture_fullscreen() -> np.ndarray:
    """捕获主显示器全屏。
    
    Returns:
        BGR 格式的 numpy 数组。
    """
    return _get_capture().capture_fullscreen()


def get_screen_size() -> Tuple[int, int]:
    """获取主显示器尺寸。
    
    Returns:
        (宽度, 高度) 元组。
    """
    return _get_capture().get_screen_size()
