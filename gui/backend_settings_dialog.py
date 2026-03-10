"""Backend settings dialog — configure DD DLL path, check Interception install, and one-click installers."""
import os
import sys
import ssl
import urllib.request
import zipfile
import tempfile
import subprocess
import shutil
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout,
    QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog,
    QMessageBox, QProgressBar, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# URLs for one-click installation
DD_URL = 'https://cdn.jsdelivr.net/gh/huiqianlu/DD_Keyboard_Mouse@master/dd64.dll'
INT_URL = 'https://github.com/oblitum/Interception/releases/download/v1.0.1/Interception.zip'


class DriverInstallerThread(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, driver_type: str, parent=None):
        super().__init__(parent)
        self.driver_type = driver_type

    def run(self):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            if self.driver_type == 'dd':
                self.log.emit('正在准备目录...')
                here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                drivers_dir = os.path.join(here, 'drivers')
                os.makedirs(drivers_dir, exist_ok=True)
                target_dll = os.path.join(drivers_dir, 'dd64.dll')

                self.log.emit('正在下载 DD驱动 (dd64.dll)...')
                with urllib.request.urlopen(DD_URL, context=ctx) as response, open(target_dll, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                
                self.log.emit('下载完成！')
                self.finished.emit(True, target_dll)

            elif self.driver_type == 'int':
                self.log.emit('安装 pyinterception 依赖...')
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinterception'])

                self.log.emit('正在下载 Interception 驱动包...')
                temp_dir = tempfile.mkdtemp()
                zip_path = os.path.join(temp_dir, 'Interception.zip')
                
                with urllib.request.urlopen(INT_URL, context=ctx) as response, open(zip_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                
                self.log.emit('解压驱动包...')
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Default interception zip structure: 
                # Interception/command line installer/install-interception.exe
                installer_path = os.path.join(temp_dir, 'Interception', 'command line installer', 'install-interception.exe')
                
                self.log.emit('准备运行内核安装程序（需要管理员权限）...')
                if sys.platform == 'win32':
                    import ctypes
                    # runas triggers UAC prompt
                    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", installer_path, "/install", None, 1)
                    if int(ret) <= 32:
                        raise RuntimeError(f'ShellExecute failed with code: {ret}')
                else:
                    self.log.emit('警告: 当前不是 Windows 系统，跳过驱动安装。')
                
                self.finished.emit(True, 'Interception 安装程序已唤起，请确认 UAC 弹窗并重启电脑生效。')

        except Exception as e:
            self.log.emit(f'发生错误: {e}')
            self.finished.emit(False, str(e))


class BackendSettingsDialog(QDialog):
    """Settings dialog for configuring input driver backends."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('输入驱动设置')
        self.setFixedSize(600, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._installer_thread: Optional[DriverInstallerThread] = None

        # Main background (cyber wave mockup)
        self.bg = QFrame(self)
        self.bg.setGeometry(0, 0, 600, 400)
        self.bg.setStyleSheet("""
            QFrame#bg {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1a1b2d, stop:0.4 #23163a, stop:0.7 #13273e, stop:1 #1a1b2d);
                border-radius: 12px;
            }
        """)
        self.bg.setObjectName("bg")
        
        main_lay = QVBoxLayout(self.bg)
        main_lay.setContentsMargins(40, 40, 40, 40)
        
        # Center Card
        self.card = QFrame()
        self.card.setStyleSheet("""
            QFrame#card {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(0, 242, 254, 0.3);
                border-top: 1px solid rgba(213, 51, 105, 0.4);
                border-border-radius: 16px;
                border-radius: 16px;
            }
        """)
        self.card.setObjectName("card")
        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(20, 20, 20, 20)
        card_lay.setSpacing(16)

        # Tabs (Pill style)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.08);
                color: #a1a1aa;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 14px;
                padding: 6px 20px;
                margin-right: 12px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7579ff, stop:1 #b224ef);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.4);
                font-weight: bold;
            }
        """)
        card_lay.addWidget(self.tabs)

        self.tabs.addTab(self._build_dd_tab(), 'DD Virtual Driver')
        self.tabs.addTab(self._build_interception_tab(), 'Interception')
        
        # When tab changes, activate the corresponding backend
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        # Set active tab based on current backend
        from core import input_backend as _ib
        curr = _ib.get_active_name()
        if curr == 'int':
            self.tabs.setCurrentIndex(1)
        else:
            self.tabs.setCurrentIndex(0)

        # Close button bottom right
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton('关闭')
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: #e4e4e7;
                border-radius: 12px;
                padding: 6px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        card_lay.addLayout(btn_row)

        main_lay.addWidget(self.card)

    def _on_tab_changed(self, idx: int):
        from core import input_backend as _ib
        if idx == 0:  # DD
            dd_path = self._dd_path_edit.text().strip()
            try:
                _ib.set_backend('dd', dll_path=dd_path)
            except Exception:
                pass
        elif idx == 1:  # Interception
            try:
                _ib.set_backend('int')
            except Exception:
                pass

    # ── common buttons ──────────────────────────────────────────────
    def _create_install_btn(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff758c, stop:1 #ff7eb3);
                border: none;
                border-radius: 16px;
                padding: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff8a9f, stop:1 #ff96c2);
            }
            QPushButton:disabled {
                background: #444; color: #888;
            }
        """)
        return btn

    def _create_check_btn(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #ced4da;
                border-radius: 16px;
                padding: 10px;
                color: #212529;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #ffffff;
            }
        """)
        return btn

    # ── DD tab ──────────────────────────────────────────────────────
    def _build_dd_tab(self) -> QWidget:
        from core.backends.dd_backend import _get_default_dll_path
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 15, 0, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        info = QLabel(
            '<b>DD Virtual Driver</b> 是内核驱动模拟输入，可绕过游戏反作弊。兼容性广，适合多等国产游戏。<br><br>'
            '点击下方按钮进行一键安装。'
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #d4d4d8; font-size: 13px; line-height: 1.5;")
        lay.addWidget(info)
        lay.addSpacing(20)

        self._btn_dd_install = self._create_install_btn('⬇ 一键下载并配置 DD Virtual Driver')
        self._btn_dd_install.clicked.connect(self._do_install_dd)
        lay.addWidget(self._btn_dd_install)
        lay.addSpacing(6)

        check_btn = self._create_check_btn('检测 DD Virtual Driver 驱动状态')
        check_btn.clicked.connect(self._check_dd)
        lay.addWidget(check_btn)
        
        # Hidden inputs for DLL path tracking. Kept for internal logic compatibility.
        self._dd_path_edit = QLineEdit()
        self._dd_path_edit.setText(_get_default_dll_path())
        self._dd_path_edit.hide()

        self._dd_status = QLabel('')
        self._dd_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dd_status.setStyleSheet("margin-top: 10px;")
        lay.addWidget(self._dd_status)

        self._check_dd()
        return w

    def _check_dd(self):
        from core.backends.dd_backend import _load_dll
        path = self._dd_path_edit.text().strip()
        if not path or not os.path.isfile(path):
            self._dd_status.setText('❌ 驱动未就绪或未安装')
            self._dd_status.setStyleSheet('color: #ef4444; font-size: 13px; font-weight: bold; margin-top: 10px;')
            return
        dll = _load_dll(path)
        if dll:
            self._dd_status.setText('✅ 驱动已安装且就绪')
            self._dd_status.setStyleSheet('color: #10b981; font-size: 13px; font-weight: bold; margin-top: 10px;')
            from core.backends import dd_backend
            dd_backend._dll_path_cache = ''
            from core import input_backend as _ib
            if _ib.get_active_name() == 'dd':
                _ib.set_backend('dd', dll_path=path)
        else:
            self._dd_status.setText('❌ 驱动未就绪或未安装')
            self._dd_status.setStyleSheet('color: #ef4444; font-size: 13px; font-weight: bold; margin-top: 10px;')

    def _do_install_dd(self):
        self._btn_dd_install.setEnabled(False)
        self._dd_status.setText('正在下载...')
        self._dd_status.setStyleSheet('color: #3b82f6; font-size: 13px; font-weight: bold; margin-top: 10px;')
        
        self._installer_thread = DriverInstallerThread('dd', self)
        self._installer_thread.log.connect(lambda msg: self._dd_status.setText(msg))
        self._installer_thread.finished.connect(self._on_dd_installed)
        self._installer_thread.start()

    def _on_dd_installed(self, success: bool, result: str):
        self._btn_dd_install.setEnabled(True)
        if success:
            self._dd_path_edit.setText(result)
            self._check_dd()
        else:
            self._dd_status.setText(f'❌ 安装失败: {result}')
            self._dd_status.setStyleSheet('color: #ef4444; font-size: 13px; font-weight: bold; margin-top: 10px;')

    # ── Interception tab ─────────────────────────────────────────────
    def _build_interception_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 15, 0, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        info = QLabel(
            'Interception 是内核驱动模拟输入，可绕过游戏反作弊。兼容性广，适合多等国产游戏。<br><br>'
            '点击下方按钮进行一键安装，安装时会有弹窗提示，安装完成后 <span style="color:#38bdf8;">必须重启系统！</span>'
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #d4d4d8; font-size: 13px; line-height: 1.5;")
        lay.addWidget(info)
        lay.addSpacing(20)

        self._btn_int_install = self._create_install_btn('⬇ 一键下载并安装 Interception')
        self._btn_int_install.clicked.connect(self._do_install_int)
        lay.addWidget(self._btn_int_install)
        lay.addSpacing(6)

        check_btn = self._create_check_btn('检测 Interception 驱动状态')
        check_btn.clicked.connect(self._check_interception)
        lay.addWidget(check_btn)

        self._int_status = QLabel('')
        self._int_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._int_status.setStyleSheet("margin-top: 10px;")
        lay.addWidget(self._int_status)

        self._check_interception()
        return w

    def _check_interception(self):
        from core.backends.interception_backend import InterceptionBackend
        if InterceptionBackend.is_available():
            self._int_status.setText('✅ 驱动已安装且就绪')
            self._int_status.setStyleSheet('color: #10b981; font-size: 13px; font-weight: bold; margin-top: 10px;')
        else:
            self._int_status.setText('❌ 驱动未就绪或未安装')
            self._int_status.setStyleSheet('color: #ef4444; font-size: 13px; font-weight: bold; margin-top: 10px;')

    def _do_install_int(self):
        self._btn_int_install.setEnabled(False)
        self._int_status.setText('准备安装...')
        self._int_status.setStyleSheet('color: #3b82f6; font-size: 13px; font-weight: bold; margin-top: 10px;')
        
        self._installer_thread = DriverInstallerThread('int', self)
        self._installer_thread.log.connect(lambda msg: self._int_status.setText(msg))
        self._installer_thread.finished.connect(self._on_int_installed)
        self._installer_thread.start()

    def _on_int_installed(self, success: bool, result: str):
        self._btn_int_install.setEnabled(True)
        if success:
            self._int_status.setText(result)
            self._int_status.setStyleSheet('color: #10b981; font-size: 13px; font-weight: bold; margin-top: 10px;')
        else:
            self._int_status.setText(f'❌ 安装失败: {result}')
            self._int_status.setStyleSheet('color: #ef4444; font-size: 13px; font-weight: bold; margin-top: 10px;')
