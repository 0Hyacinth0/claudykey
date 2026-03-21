"""EasyOCR wrapper for GPU-accelerated text recognition.

提供 OCR 文字识别功能，支持 GPU 加速。
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional

from .logger import get_logger

logger = get_logger(__name__)


class OCREngine:
    """OCR 引擎单例类。
    
    使用单例模式管理 EasyOCR Reader 实例，
    避免重复加载模型。
    """
    
    _instance: Optional['OCREngine'] = None
    _reader: Optional[object] = None
    
    def __new__(cls) -> 'OCREngine':
        """确保单例实例唯一性。"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _initialize_reader(self) -> None:
        """初始化 EasyOCR Reader。
        
        Raises:
            ImportError: EasyOCR 未安装。
            RuntimeError: GPU 初始化失败。
        """
        if self._reader is not None:
            return
        
        try:
            import easyocr
            logger.info("正在初始化 EasyOCR 模型 (GPU 加速)...")
            self._reader = easyocr.Reader(
                ['ch_sim', 'en'],
                gpu=True,
                verbose=False
            )
            logger.info("EasyOCR 模型初始化完成")
        except ImportError as e:
            logger.error("EasyOCR 未安装，请运行: pip install easyocr")
            raise ImportError(
                "EasyOCR 未安装。请运行: pip install easyocr"
            ) from e
        except Exception as e:
            logger.error(f"EasyOCR 初始化失败: {e}")
            raise RuntimeError(f"OCR 引擎初始化失败: {e}") from e
    
    @property
    def reader(self) -> object:
        """获取 EasyOCR Reader 实例。
        
        Returns:
            EasyOCR Reader 实例。
        """
        if self._reader is None:
            self._initialize_reader()
        return self._reader
    
    def recognize(self, image: np.ndarray, allowlist: Optional[str] = None) -> List[Tuple[list, str, float]]:
        """识别图像中的文字。
        
        Args:
            image: BGR 格式的图像数组。
            
        Returns:
            识别结果列表，每个元素为 (bbox, text, confidence) 元组。
            
        Raises:
            ValueError: 图像格式无效。
            RuntimeError: OCR 识别失败。
        """
        if image is None or image.size == 0:
            raise ValueError("图像不能为空")
        
        try:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            rgb = cv2.resize(rgb, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
            
            if allowlist:
                results = self.reader.readtext(rgb, allowlist=allowlist)
            else:
                results = self.reader.readtext(rgb)
            
            logger.debug(f"OCR 识别完成，发现 {len(results)} 个文本区域")
            return results
        except cv2.error as e:
            logger.error(f"图像颜色转换失败: {e}")
            raise ValueError(f"图像格式无效: {e}") from e
        except Exception as e:
            logger.error(f"OCR 识别失败: {e}")
            raise RuntimeError(f"OCR 识别失败: {e}") from e
    
    def recognize_text_only(self, image: np.ndarray, allowlist: Optional[str] = None) -> str:
        """识别图像中的文字并返回拼接后的字符串。
        
        Args:
            image: BGR 格式的图像数组。
            allowlist: 允许识别出的字符集合，如 '0123456789.-%:/ '
        
        Returns:
            所有识别文字拼接后的字符串。
        """
        results = self.recognize(image, allowlist=allowlist)
        text = ' '.join(r[1] for r in results)
        return text
    
    def is_ready(self) -> bool:
        """检查 OCR 引擎是否已初始化。
        
        Returns:
            如果已初始化返回 True，否则返回 False。
        """
        return self._reader is not None


_engine: Optional[OCREngine] = None


def _get_engine() -> OCREngine:
    """获取 OCR 引擎单例实例。
    
    Returns:
        OCREngine 实例。
    """
    global _engine
    if _engine is None:
        _engine = OCREngine()
    return _engine


def recognize(image: np.ndarray, allowlist: Optional[str] = None) -> List[Tuple[list, str, float]]:
    """识别图像中的文字。
    
    Args:
        image: BGR 格式的图像数组。
        allowlist: 可选，允许识别的字符。
        
    Returns:
        识别结果列表，每个元素为 (bbox, text, confidence) 元组。
    """
    return _get_engine().recognize(image, allowlist=allowlist)


def recognize_text_only(image: np.ndarray, allowlist: Optional[str] = None) -> str:
    """识别图像中的文字并返回拼接后的字符串。
    
    Args:
        image: BGR 格式的图像数组。
        allowlist: 可选，允许识别的字符。
        
    Returns:
        所有识别文字拼接后的字符串。
    """
    return _get_engine().recognize_text_only(image, allowlist=allowlist)


def is_ready() -> bool:
    """检查 OCR 引擎是否已初始化。
    
    Returns:
        如果已初始化返回 True，否则返回 False。
    """
    return _get_engine().is_ready()


def warm_up() -> None:
    """预热 OCR 引擎。
    
    在程序启动时调用，避免首次使用时的延迟。
    """
    logger.info("预热 OCR 引擎...")
    _get_engine()._initialize_reader()
