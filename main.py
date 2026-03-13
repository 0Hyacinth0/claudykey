"""ClaudyKey — AI-powered macro clicker entry point.

ClaudyKey 主入口文件，负责初始化日志系统和启动 GUI。
"""
import sys
import os
import threading
import platform

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QSplashScreen, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QTimer, qInstallMessageHandler, QtMsgType
from PyQt6.QtGui import QFont

from gui.theme import THEME_QSS
from core.logger import setup_logging, get_logger, get_default_log_file


def _warm_up_ocr():
    """Pre-load EasyOCR model in background so first use is instant.
    
    在后台线程中预热 OCR 模型，避免首次使用时的延迟。
    """
    logger = get_logger(__name__)
    try:
        logger.info("开始预热 OCR 模型...")
        from core import ocr
        ocr.warm_up()
        logger.info("OCR 模型预热完成")
    except ImportError as e:
        logger.warning(f"EasyOCR 未安装，跳过预热: {e}")
    except RuntimeError as e:
        logger.error(f"OCR 模型预热失败: {e}")
    except Exception as e:
        logger.error(f"OCR 预热时发生未知错误: {e}")


def _qt_message_handler(mode, context, message):
    """Qt 消息处理器，过滤掉 ICC profile 警告。
    
    Args:
        mode: Qt 消息类型。
        context: 消息上下文。
        message: 消息内容。
    """
    if "iCCP" in message or "incorrect sRGB profile" in message:
        return
    sys.stderr.write(f"{message}\n")


def _check_platform():
    """检查平台兼容性。
    
    ClaudyKey 主要为 Windows 设计，使用 Windows 专用的内核驱动。
    
    Returns:
        bool: 如果平台支持返回 True，否则返回 False。
    """
    current_platform = platform.system()
    if current_platform != 'Windows':
        logger = get_logger(__name__)
        logger.warning(f"检测到非 Windows 平台: {current_platform}")
        logger.warning("ClaudyKey 的核心功能（DD驱动、Interception驱动）仅支持 Windows")
        logger.warning("部分功能可能无法正常工作")
        return False
    return True


def main():
    """主函数，初始化并启动 ClaudyKey 应用程序。"""
    setup_logging(
        log_level=20,
        log_file=get_default_log_file(),
        log_to_console=True
    )
    
    logger = get_logger(__name__)
    logger.info("=" * 50)
    logger.info("ClaudyKey 启动中...")
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"平台: {platform.system()} {platform.release()}")
    logger.info("=" * 50)
    
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    qInstallMessageHandler(_qt_message_handler)

    app.setApplicationName('ClaudyKey')
    app.setApplicationDisplayName('ClaudyKey')
    app.setStyle('Fusion')
    app.setStyleSheet(THEME_QSS)

    splash = QSplashScreen()
    splash.setFixedSize(420, 200)
    splash.setStyleSheet("""
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #fff0f5, stop:1 #ffe6ee);
        border: 1px solid #f2c2d6;
        border-radius: 10px;
    """)
    splash_lbl = QLabel(splash)
    splash_lbl.setGeometry(0, 0, 420, 200)
    splash_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    splash_lbl.setText(
        '<span style="color:#d15c89;font-size:32px;font-weight:bold;">'
        '⌨ ClaudyKey</span><br>'
        '<br><span style="color:#9c7b8c;font-size:13px;">AI 智能连点器  正在启动…</span>'
    )
    splash_lbl.setTextFormat(Qt.TextFormat.RichText)
    splash.show()
    app.processEvents()

    _check_platform()

    threading.Thread(target=_warm_up_ocr, daemon=True).start()

    try:
        from gui.main_window import MainWindow
        window = MainWindow()
        logger.info("主窗口创建成功")
    except ImportError as e:
        logger.critical(f"导入主窗口失败: {e}")
        QMessageBox.critical(
            None,
            '启动失败',
            f'无法加载主窗口模块:\n{e}\n\n请检查依赖是否正确安装。'
        )
        sys.exit(1)
    except Exception as e:
        logger.critical(f"创建主窗口失败: {e}", exc_info=True)
        QMessageBox.critical(
            None,
            '启动失败',
            f'创建主窗口时发生错误:\n{e}'
        )
        sys.exit(1)

    def _show():
        splash.finish(window)
        window.show()
        logger.info("ClaudyKey 启动完成")

    QTimer.singleShot(800, _show)
    
    exit_code = app.exec()
    logger.info(f"ClaudyKey 退出，代码: {exit_code}")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
