"""OpenCV template matching for icon/image detection on screen.

提供图像模板匹配功能，使用 OpenCV 实现。
"""
import cv2
import numpy as np
from typing import Optional, Tuple, List

from .logger import get_logger

logger = get_logger(__name__)


class ImageMatcher:
    """图像匹配器类。
    
    提供模板加载和匹配功能。
    """
    
    def load_template(self, path: str) -> np.ndarray:
        """加载模板图像。
        
        使用 PIL 加载图像以避免 OpenCV 的 ICC profile 警告。
        
        Args:
            path: 模板图像文件路径。
            
        Returns:
            BGR 格式的 numpy 数组。
            
        Raises:
            FileNotFoundError: 文件不存在。
            ValueError: 图像格式无效。
            RuntimeError: 加载失败。
        """
        if not path:
            raise ValueError("模板路径不能为空")
        
        try:
            from PIL import Image
            with Image.open(path) as pil_img:
                img = np.array(pil_img.convert('RGB'))[:, :, ::-1].copy()
                logger.debug(f"模板加载成功: {path}, 尺寸: {img.shape}")
                return img
        except FileNotFoundError:
            logger.error(f"模板文件不存在: {path}")
            raise FileNotFoundError(f"模板文件不存在: {path}") from None
        except Exception as e:
            logger.error(f"使用 PIL 加载模板失败: {path}, 错误: {e}")
            
            try:
                img = cv2.imread(path)
                if img is None:
                    raise FileNotFoundError(f"无法加载模板图像: {path}")
                logger.debug(f"使用 OpenCV 加载模板成功: {path}")
                return img
            except cv2.error as e:
                logger.error(f"OpenCV 加载模板失败: {path}, 错误: {e}")
                raise RuntimeError(f"无法加载模板图像: {path}") from e
    
    def find_template(
        self,
        screen: np.ndarray,
        template: np.ndarray,
        threshold: float = 0.80
    ) -> Optional[Tuple[int, int, float]]:
        """在屏幕图像中查找模板。
        
        使用归一化互相关方法进行模板匹配。
        
        Args:
            screen: 屏幕截图 (BGR 格式)。
            template: 模板图像 (BGR 格式)。
            threshold: 匹配阈值，范围 0-1，默认 0.80。
            
        Returns:
            如果找到，返回 (中心X, 中心Y, 置信度) 元组；
            否则返回 None。
            
        Raises:
            ValueError: 参数无效。
        """
        if screen is None or screen.size == 0:
            raise ValueError("屏幕图像不能为空")
        if template is None or template.size == 0:
            raise ValueError("模板图像不能为空")
        if not 0 <= threshold <= 1:
            raise ValueError(f"阈值必须在 0-1 之间: {threshold}")
        
        if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
            logger.debug("模板尺寸大于屏幕尺寸，跳过匹配")
            return None
        
        try:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                h, w = template.shape[:2]
                cx = max_loc[0] + w // 2
                cy = max_loc[1] + h // 2
                logger.debug(f"模板匹配成功: 位置({cx}, {cy}), 置信度: {max_val:.3f}")
                return (cx, cy, float(max_val))
            
            logger.debug(f"模板匹配失败: 最高置信度 {max_val:.3f} < 阈值 {threshold}")
            return None
        except cv2.error as e:
            logger.error(f"模板匹配 OpenCV 错误: {e}")
            return None
    
    def find_all_templates(
        self,
        screen: np.ndarray,
        template: np.ndarray,
        threshold: float = 0.80
    ) -> List[Tuple[int, int, float]]:
        """查找屏幕中所有匹配的模板位置。
        
        Args:
            screen: 屏幕截图 (BGR 格式)。
            template: 模板图像 (BGR 格式)。
            threshold: 匹配阈值，范围 0-1，默认 0.80。
            
        Returns:
            匹配结果列表，每个元素为 (中心X, 中心Y, 置信度) 元组。
        """
        if screen is None or screen.size == 0:
            raise ValueError("屏幕图像不能为空")
        if template is None or template.size == 0:
            raise ValueError("模板图像不能为空")
        
        if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
            return []
        
        try:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            locs = np.where(result >= threshold)
            h, w = template.shape[:2]
            matches = []
            
            for pt in zip(*locs[::-1]):
                cx = pt[0] + w // 2
                cy = pt[1] + h // 2
                conf = float(result[pt[1], pt[0]])
                matches.append((cx, cy, conf))
            
            logger.debug(f"找到 {len(matches)} 个匹配位置")
            return matches
        except cv2.error as e:
            logger.error(f"批量模板匹配 OpenCV 错误: {e}")
            return []


_matcher: Optional[ImageMatcher] = None


def _get_matcher() -> ImageMatcher:
    """获取图像匹配器单例实例。
    
    Returns:
        ImageMatcher 实例。
    """
    global _matcher
    if _matcher is None:
        _matcher = ImageMatcher()
    return _matcher


def load_template(path: str) -> np.ndarray:
    """加载模板图像。
    
    Args:
        path: 模板图像文件路径。
        
    Returns:
        BGR 格式的 numpy 数组。
    """
    return _get_matcher().load_template(path)


def find_template(
    screen: np.ndarray,
    template: np.ndarray,
    threshold: float = 0.80
) -> Optional[Tuple[int, int, float]]:
    """在屏幕图像中查找模板。
    
    Args:
        screen: 屏幕截图 (BGR 格式)。
        template: 模板图像 (BGR 格式)。
        threshold: 匹配阈值，范围 0-1，默认 0.80。
        
    Returns:
        如果找到，返回 (中心X, 中心Y, 置信度) 元组；
        否则返回 None。
    """
    return _get_matcher().find_template(screen, template, threshold)


def find_all_templates(
    screen: np.ndarray,
    template: np.ndarray,
    threshold: float = 0.80
) -> List[Tuple[int, int, float]]:
    """查找屏幕中所有匹配的模板位置。
    
    Args:
        screen: 屏幕截图 (BGR 格式)。
        template: 模板图像 (BGR 格式)。
        threshold: 匹配阈值，范围 0-1，默认 0.80。
        
    Returns:
        匹配结果列表，每个元素为 (中心X, 中心Y, 置信度) 元组。
    """
    return _get_matcher().find_all_templates(screen, template, threshold)
