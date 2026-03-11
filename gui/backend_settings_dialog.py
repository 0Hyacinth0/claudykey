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
    QMessageBox, QProgressBar, QComboBox
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
                self.log.emit('安装 interception-python 依赖...')
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'interception-python'])

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
                installer_path = os.path.abspath(installer_path)
                
                self.log.emit('准备运行内核安装程序（需要管理员权限）...')
                if sys.platform == 'win32':
                    import ctypes
                    
                    # Create a wrapper batch file so we can pause and see the output
                    bat_path = os.path.join(temp_dir, 'Interception', 'command line installer', 'install_wrapper.bat')
                    with open(bat_path, 'w', encoding='utf-8') as f:
                        f.write('@echo off\n')
                        f.write('cd /d "%~dp0"\n')
                        f.write('echo 正在安装 Interception 内核驱动...\n')
                        f.write('install-interception.exe /install\n')
                        f.write('echo.\n')
                        f.write('echo 安装完成（如果上方没有报错，说明成功）。操作完毕后必须重启电脑生效！\n')
                        f.write('pause\n')
                        
                    # runas triggers UAC prompt and executes the batch file
                    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", bat_path, "", None, 1)
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
        self.setMinimumSize(480, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._installer_thread: Optional[DriverInstallerThread] = None
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        
        # Active backend selector
        top_lay = QHBoxLayout()
        top_lay.addWidget(QLabel('当前使用驱动:'))
        self._combo_backend = QComboBox()
        self._combo_backend.addItem('DD虚拟驱动', 'dd')
        self._combo_backend.addItem('Interception拦截器', 'int')
        
        from core import input_backend as _ib
        curr = _ib.get_active_name()
        if curr == 'int':
            self._combo_backend.setCurrentIndex(1)
        else:
            self._combo_backend.setCurrentIndex(0)
            
        self._combo_backend.currentIndexChanged.connect(self._on_backend_changed)
        top_lay.addWidget(self._combo_backend, 1)
        lay.addLayout(top_lay)
        lay.addSpacing(4)

        self.tabs = QTabWidget()
        lay.addWidget(self.tabs)

        self.tabs.addTab(self._build_dd_tab(), 'DD虚拟驱动')
        self.tabs.addTab(self._build_interception_tab(), 'Interception')

        # Link active backend combo to tab index (optional UX improvement)
        self._combo_backend.currentIndexChanged.connect(self.tabs.setCurrentIndex)
        self.tabs.currentChanged.connect(self._combo_backend.setCurrentIndex)

        # Close button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        lay.addLayout(btn_row)

    def _on_backend_changed(self, idx: int):
        from core import input_backend as _ib
        backend_name = self._combo_backend.itemData(idx)
        if backend_name == 'dd':
            dd_path = self._dd_path_edit.text().strip()
            try:
                _ib.set_backend('dd', dll_path=dd_path)
            except Exception as e:
                pass
        elif backend_name == 'int':
            try:
                _ib.set_backend('int')
            except Exception as e:
                pass

    # ── DD tab ──────────────────────────────────────────────────────
    def _build_dd_tab(self) -> QWidget:
        from core.backends.dd_backend import _get_default_dll_path
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        info = QLabel(
            '<b>DD虚拟驱动</b> 通过内核驱动模拟输入，可绕过游戏反作弊。<br>'
            '适合 <b>剑网3、DNF</b> 等国产游戏。<br><br>'
            '自动下载可能因源仓库失效而失败（HTTP 404）。<br>'
            '如果遇到下载失败，请<b>手动在网上搜索并下载 "dd64.dll"</b>，然后将其路径填在下方。'
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(info)
        lay.addSpacing(8)

        # One click install button
        self._btn_dd_install = QPushButton('⬇️ 一键下载并配置 DD 驱动')
        self._btn_dd_install.setObjectName('btn_test_macro')
        self._btn_dd_install.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_dd_install.clicked.connect(self._do_install_dd)
        lay.addWidget(self._btn_dd_install)
        lay.addSpacing(12)

        form = QFormLayout()
        self._dd_path_edit = QLineEdit()
        self._dd_path_edit.setPlaceholderText('例: C:\\tools\\dd64.dll')
        self._dd_path_edit.setText(_get_default_dll_path())

        path_row = QHBoxLayout()
        path_row.addWidget(self._dd_path_edit)
        browse_btn = QPushButton('浏览…')
        browse_btn.setFixedWidth(60)
        browse_btn.clicked.connect(self._browse_dd_dll)
        path_row.addWidget(browse_btn)

        form.addRow('DLL 路径:', path_row)
        lay.addLayout(form)

        check_btn = QPushButton('检测 DD 驱动')
        check_btn.clicked.connect(self._check_dd)
        lay.addWidget(check_btn)

        self._dd_status = QLabel('')
        lay.addWidget(self._dd_status)

        self._check_dd()
        return w

    def _browse_dd_dll(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '选择 DD 驱动 DLL', '', 'DLL 文件 (*.dll)')
        if path:
            self._dd_path_edit.setText(path)

    def _check_dd(self):
        from core.backends.dd_backend import DDBackend
        path = self._dd_path_edit.text().strip()
        if not path:
            self._dd_status.setText('⚠ 未指定DLL路径')
            self._dd_status.setStyleSheet('color:#d6871a;')
            return
        if not os.path.isfile(path):
            self._dd_status.setText('❌ 文件不存在')
            self._dd_status.setStyleSheet('color:#d94141;')
            return
        
        # Test loading the backend
        test_backend = DDBackend(dll_path=path)
        
        if test_backend._dll:
            self._dd_status.setText('✅ 驱动可用')
            self._dd_status.setStyleSheet('color:#1fa357; font-weight:bold;')
            from core import input_backend as _ib
            if _ib.get_active_name() == 'dd':
                _ib.set_backend('dd', dll_path=path)
        else:
            self._dd_status.setText('❌ DLL加载失败（可能位数不匹配或驱动未安装）')
            self._dd_status.setStyleSheet('color:#d94141;')

    def _do_install_dd(self):
        self._btn_dd_install.setEnabled(False)
        self._dd_status.setText('正在下载...')
        self._dd_status.setStyleSheet('color:#1fa357;')
        
        self._installer_thread = DriverInstallerThread('dd', self)
        self._installer_thread.log.connect(lambda msg: self._dd_status.setText(msg))
        self._installer_thread.finished.connect(self._on_dd_installed)
        self._installer_thread.start()

    def _on_dd_installed(self, success: bool, result: str):
        self._btn_dd_install.setEnabled(True)
        if success:
            self._dd_path_edit.setText(result)
            self._check_dd()
            QMessageBox.information(self, 'DD 驱动下载完成', 'DD驱动下载并配置成功！当前已可用。')
        else:
            if '404' in result or 'Not Found' in result:
                QMessageBox.critical(self, '下载失败', '自动下载源已失效 (HTTP 404)。\n\n请手动在网上搜索并下载 "dd64.dll"，然后使用上方【浏览】按钮选择该文件。')
            else:
                QMessageBox.critical(self, '安装失败', f'下载或配置 DD 驱动失败:\n{result}')

    # ── Interception tab ─────────────────────────────────────────────
    def _build_interception_tab(self) -> QWidget:
        from core.backends.interception_backend import InterceptionBackend
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        info = QLabel(
            '<b>Interception</b> 是开源内核驱动，支持按扫描码发送输入，<br>'
            '兼容性广，适合 <b>外服游戏及需要严格穿透的场景</b>。<br><br>'
            '点击下方按钮进行一键安装，安装时会有弹窗提示，<b>安装完成后必须重启系统！</b>'
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(info)
        lay.addSpacing(8)

        # One click install button
        self._btn_int_install = QPushButton('⬇️ 一键下载并安装 Interception')
        self._btn_int_install.setObjectName('btn_test_macro')
        self._btn_int_install.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_int_install.clicked.connect(self._do_install_int)
        lay.addWidget(self._btn_int_install)
        lay.addSpacing(12)

        check_btn = QPushButton('检测 Interception 驱动状态')
        check_btn.clicked.connect(self._check_interception)
        lay.addWidget(check_btn)

        self._int_status = QLabel('')
        lay.addWidget(self._int_status)

        self._check_interception()
        return w

    def _check_interception(self):
        from core.backends.interception_backend import InterceptionBackend
        if InterceptionBackend.is_available():
            self._int_status.setText('✅ 驱动已安装，可用')
            self._int_status.setStyleSheet('color:#1fa357; font-weight:bold;')
        else:
            self._int_status.setText('❌ 驱动未就绪或未安装')
            self._int_status.setStyleSheet('color:#d94141;')

    def _do_install_int(self):
        self._btn_int_install.setEnabled(False)
        self._int_status.setText('准备安装...')
        self._int_status.setStyleSheet('color:#1fa357;')
        
        self._installer_thread = DriverInstallerThread('int', self)
        self._installer_thread.log.connect(lambda msg: self._int_status.setText(msg))
        self._installer_thread.finished.connect(self._on_int_installed)
        self._installer_thread.start()

    def _on_int_installed(self, success: bool, result: str):
        self._btn_int_install.setEnabled(True)
        if success:
            QMessageBox.information(self, 'Interception 安装', result)
            self._check_interception()
        else:
            QMessageBox.critical(self, '安装失败', f'安装 Interception 驱动失败:\n{result}')
