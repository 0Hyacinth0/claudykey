"""Backend settings dialog — configure DD DLL path, check Interception install, and one-click installers.

DD驱动说明:
    DD驱动由两部分组成:
    1. 内核驱动 (dd.sys) - 需要以管理员身份安装到 Windows 内核
    2. 用户态DLL (dd64.dll) - 应用程序通过它调用内核驱动

    仅下载 DLL 是不够的，必须先安装内核驱动才能正常工作。
"""
import os
import sys
import ssl
import urllib.request
import zipfile
import tempfile
import subprocess
import shutil
import ctypes
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout,
    QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog,
    QMessageBox, QProgressBar, QComboBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

DD_URL = 'https://cdn.jsdelivr.net/gh/huiqianlu/DD_Keyboard_Mouse@master/dd64.dll'
DD_DRIVER_URL = 'https://github.com/66maer/pydd/raw/main/dd.54900.dll'
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
                here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                target_dir = os.path.join(here, 'drivers', 'InterceptionInstaller')
                os.makedirs(target_dir, exist_ok=True)
                temp_dir = target_dir
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
                
                # instead of trying to automate the buggy older exe via shell, we just open the folder
                # and explicitly instruct the user how to install it locally.
                self.finished.emit(True, f'{os.path.join(temp_dir, "Interception", "command line installer")}')

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
        """切换驱动后端时的处理函数。
        
        Args:
            idx: 下拉框选中项的索引。
        """
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
        """构建 DD 驱动设置标签页。
        
        Returns:
            QWidget: DD 驱动设置页面组件。
        """
        from core.backends.dd_backend import _get_default_dll_path
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        info_group = QGroupBox('DD驱动说明')
        info_lay = QVBoxLayout(info_group)
        info = QLabel(
            '<b>DD虚拟驱动</b> 是一款内核级输入模拟驱动，可绕过大多数游戏的反作弊检测。<br><br>'
            '<b>⚠️ 重要：DD驱动由两部分组成，缺一不可！</b><br>'
            '1. <b>内核驱动 (dd.sys)</b> - 需要以管理员身份安装<br>'
            '2. <b>用户态DLL (dd64.dll)</b> - 本程序通过它调用驱动<br><br>'
            '仅下载 DLL 文件是<b>不够的</b>，必须先安装内核驱动！'
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        info_lay.addWidget(info)
        lay.addWidget(info_group)
        lay.addSpacing(8)

        install_group = QGroupBox('安装步骤')
        install_lay = QVBoxLayout(install_group)
        steps = QLabel(
            '<b>第一步：下载驱动包</b><br>'
            '• 点击下方「下载 DD 驱动 DLL」按钮<br><br>'
            '<b>第二步：安装内核驱动</b><br>'
            '• 以<b>管理员身份</b>运行命令提示符<br>'
            '• 执行: <code>regsvr32 dd64.dll</code> 或使用驱动自带的安装程序<br>'
            '• 部分版本需要运行 <code>install.bat</code> 或 <code>驱动安装.exe</code><br><br>'
            '<b>第三步：重启电脑</b><br>'
            '• 安装完成后<b>必须重启系统</b>才能生效<br><br>'
            '<b>第四步：验证安装</b><br>'
            '• 重启后点击下方「检测 DD 驱动」验证是否成功'
        )
        steps.setWordWrap(True)
        steps.setTextFormat(Qt.TextFormat.RichText)
        install_lay.addWidget(steps)
        lay.addWidget(install_group)
        lay.addSpacing(8)

        btn_row = QHBoxLayout()
        self._btn_dd_install = QPushButton('⬇️ 下载 DD 驱动 DLL')
        self._btn_dd_install.setObjectName('btn_test_macro')
        self._btn_dd_install.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_dd_install.clicked.connect(self._do_install_dd)
        btn_row.addWidget(self._btn_dd_install)

        check_btn = QPushButton('🔍 检测 DD 驱动')
        check_btn.clicked.connect(self._check_dd)
        btn_row.addWidget(check_btn)
        lay.addLayout(btn_row)

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

        self._dd_status = QLabel('')
        self._dd_status.setWordWrap(True)
        lay.addWidget(self._dd_status)

        self._check_dd()
        return w

    def _browse_dd_dll(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '选择 DD 驱动 DLL', '', 'DLL 文件 (*.dll)')
        if path:
            self._dd_path_edit.setText(path)

    def _check_dd(self):
        """检测 DD 驱动状态，提供详细的诊断信息。"""
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
        
        if sys.platform != 'win32':
            self._dd_status.setText('❌ DD驱动仅支持 Windows 系统')
            self._dd_status.setStyleSheet('color:#d94141;')
            return
        
        try:
            test_backend = DDBackend(dll_path=path)
        except Exception as e:
            self._dd_status.setText(f'❌ DLL 加载异常: {e}')
            self._dd_status.setStyleSheet('color:#d94141;')
            return
        
        if not test_backend._dll:
            self._dd_status.setText(
                '❌ DLL 加载失败\n'
                '可能原因:\n'
                '• 32位/64位不匹配（请使用与Python相同位数的DLL）\n'
                '• DLL 文件损坏\n'
                '• 缺少运行时依赖'
            )
            self._dd_status.setStyleSheet('color:#d94141;')
            return
        
        if test_backend.test_connection():
            self._dd_status.setText('✅ 驱动可用 - 内核驱动已正确安装并运行')
            self._dd_status.setStyleSheet('color:#1fa357; font-weight:bold;')
            from core import input_backend as _ib
            if _ib.get_active_name() == 'dd':
                _ib.set_backend('dd', dll_path=path)
        else:
            self._dd_status.setText(
                '⚠️ DLL 已加载，但内核驱动未响应\n\n'
                '这通常意味着内核驱动 (dd.sys) 未安装！\n\n'
                '请按以下步骤操作:\n'
                '1. 以管理员身份打开命令提示符\n'
                '2. 执行驱动安装程序或 install.bat\n'
                '3. 重启电脑后再试'
            )
            self._dd_status.setStyleSheet('color:#d6871a;')

    def _do_install_dd(self):
        self._btn_dd_install.setEnabled(False)
        self._dd_status.setText('正在下载...')
        self._dd_status.setStyleSheet('color:#1fa357;')
        
        self._installer_thread = DriverInstallerThread('dd', self)
        self._installer_thread.log.connect(lambda msg: self._dd_status.setText(msg))
        self._installer_thread.finished.connect(self._on_dd_installed)
        self._installer_thread.start()

    def _on_dd_installed(self, success: bool, result: str):
        """DD 驱动下载完成后的回调处理。
        
        Args:
            success: 下载是否成功。
            result: 成功时为文件路径，失败时为错误信息。
        """
        self._btn_dd_install.setEnabled(True)
        if success:
            self._dd_path_edit.setText(result)
            self._check_dd()
            QMessageBox.information(
                self, 
                'DD 驱动 DLL 下载完成', 
                f'DLL 文件已下载到:\n{result}\n\n'
                '⚠️ 重要提示：\n'
                '下载的只是 DLL 文件，你还需要安装内核驱动！\n\n'
                '请按照界面上的「安装步骤」操作：\n'
                '1. 以管理员身份运行驱动安装程序\n'
                '2. 重启电脑\n'
                '3. 再次点击「检测 DD 驱动」验证'
            )
        else:
            if '404' in result or 'Not Found' in result:
                QMessageBox.critical(
                    self, 
                    '下载失败', 
                    '自动下载源已失效 (HTTP 404)。\n\n'
                    '请手动下载 DD 驱动:\n'
                    '1. 搜索 "DD虚拟驱动" 或 "dd64.dll"\n'
                    '2. 从可靠来源下载完整驱动包\n'
                    '3. 使用上方【浏览】按钮选择 DLL 文件'
                )
            else:
                QMessageBox.critical(self, '下载失败', f'下载 DD 驱动失败:\n{result}')

    def _build_interception_tab(self) -> QWidget:
        """构建 Interception 驱动设置标签页。
        
        Returns:
            QWidget: Interception 驱动设置页面组件。
        """
        from core.backends.interception_backend import InterceptionBackend
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        info_group = QGroupBox('Interception 驱动说明')
        info_lay = QVBoxLayout(info_group)
        info = QLabel(
            '<b>Interception</b> 是一款开源的内核级输入拦截/模拟驱动。<br><br>'
            '特点：<br>'
            '• 开源免费，社区活跃<br>'
            '• 支持按扫描码发送输入，兼容性广<br>'
            '• 适合外服游戏及需要严格穿透的场景<br><br>'
            '<b>⚠️ 安装后必须重启系统才能生效！</b>'
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        info_lay.addWidget(info)
        lay.addWidget(info_group)
        lay.addSpacing(8)

        install_group = QGroupBox('安装步骤')
        install_lay = QVBoxLayout(install_group)
        steps = QLabel(
            '<b>第一步：安装 Python 依赖</b><br>'
            '• 点击下方按钮会自动安装 interception-python<br><br>'
            '<b>第二步：下载并安装驱动</b><br>'
            '• 点击按钮后会下载驱动包并打开安装目录<br>'
            '• 以<b>管理员身份</b>运行 <code>install-interception.exe</code><br><br>'
            '<b>第三步：重启电脑</b><br>'
            '• 安装完成后<b>必须重启系统</b><br><br>'
            '<b>注意：</b>某些系统可能需要关闭驱动强制签名验证'
        )
        steps.setWordWrap(True)
        steps.setTextFormat(Qt.TextFormat.RichText)
        install_lay.addWidget(steps)
        lay.addWidget(install_group)
        lay.addSpacing(8)

        btn_row = QHBoxLayout()
        self._btn_int_install = QPushButton('⬇️ 一键下载并安装 Interception')
        self._btn_int_install.setObjectName('btn_test_macro')
        self._btn_int_install.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_int_install.clicked.connect(self._do_install_int)
        btn_row.addWidget(self._btn_int_install)

        check_btn = QPushButton('🔍 检测驱动状态')
        check_btn.clicked.connect(self._check_interception)
        btn_row.addWidget(check_btn)
        lay.addLayout(btn_row)

        self._int_status = QLabel('')
        self._int_status.setWordWrap(True)
        lay.addWidget(self._int_status)

        self._check_interception()
        return w

    def _check_interception(self):
        """检测 Interception 驱动状态。"""
        from core.backends.interception_backend import InterceptionBackend
        if InterceptionBackend.is_available():
            self._int_status.setText('✅ 驱动已安装并可用')
            self._int_status.setStyleSheet('color:#1fa357; font-weight:bold;')
        else:
            self._int_status.setText(
                '❌ 驱动未就绪\n\n'
                '可能原因:\n'
                '• Interception 驱动未安装\n'
                '• interception-python 包未安装\n'
                '• 安装后未重启系统\n\n'
                '请按照安装步骤操作后重试'
            )
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
