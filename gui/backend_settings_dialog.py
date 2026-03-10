"""Backend settings dialog — configure DD DLL path, check Interception install."""
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout,
    QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog,
    QTextEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class BackendSettingsDialog(QDialog):
    """Settings dialog for configuring input driver backends."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('输入驱动设置')
        self.setMinimumSize(480, 360)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        self.tabs = QTabWidget()
        lay.addWidget(self.tabs)

        self.tabs.addTab(self._build_pynput_tab(), 'pynput（默认）')
        self.tabs.addTab(self._build_dd_tab(), 'DD虚拟驱动')
        self.tabs.addTab(self._build_interception_tab(), 'Interception')

        # Close button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        lay.addLayout(btn_row)

    # ── pynput tab ──────────────────────────────────────────────────
    def _build_pynput_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lbl = QLabel(
            '<b>pynput</b> 是默认输入后端，无需额外安装。<br><br>'
            '使用 Windows SendInput API，<b>适合普通场景</b>，但部分游戏反作弊会屏蔽此方式。<br>'
            '如在游戏中无效，请切换为 DD虚拟驱动 或 Interception驱动。'
        )
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.TextFormat.RichText)

        status = QLabel('✅ 当前可用')
        status.setStyleSheet('color: #1fa357; font-weight: bold;')
        lay.addWidget(lbl)
        lay.addSpacing(12)
        lay.addWidget(status)
        return w

    # ── DD tab ──────────────────────────────────────────────────────
    def _build_dd_tab(self) -> QWidget:
        from core.backends.dd_backend import _get_default_dll_path, _load_dll
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        info = QLabel(
            '<b>DD虚拟驱动</b> 通过内核驱动模拟输入，可绕过游戏反作弊。<br>'
            '适合 <b>剑网3、DNF</b> 等国产游戏。<br><br>'
            '下载地址：<a href="https://www.ddxoft.com/">www.ddxoft.com</a><br>'
            '下载后将 <code>dd64.dll</code>（64位）或 <code>dd.dll</code>（32位）<br>'
            '放入项目 <code>drivers/</code> 目录，或在下方手动指定路径。'
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        info.setOpenExternalLinks(True)
        lay.addWidget(info)
        lay.addSpacing(8)

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

        # Trigger an initial status check
        self._check_dd()
        return w

    def _browse_dd_dll(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '选择 DD 驱动 DLL', '', 'DLL 文件 (*.dll)')
        if path:
            self._dd_path_edit.setText(path)

    def _check_dd(self):
        from core.backends.dd_backend import _load_dll
        path = self._dd_path_edit.text().strip()
        if not path:
            self._dd_status.setText('⚠ 未指定DLL路径')
            self._dd_status.setStyleSheet('color:#d6871a;')
            return
        if not os.path.isfile(path):
            self._dd_status.setText('❌ 文件不存在')
            self._dd_status.setStyleSheet('color:#d94141;')
            return
        dll = _load_dll(path)
        if dll:
            self._dd_status.setText('✅ 驱动可用')
            self._dd_status.setStyleSheet('color:#1fa357; font-weight:bold;')
            # Persist path for this session
            from core.backends import dd_backend
            dd_backend._dll_path_cache = ''  # force reload
            from core import input_backend as _ib
            if _ib.get_active_name() == 'dd':
                _ib.set_backend('dd', dll_path=path)
        else:
            self._dd_status.setText('❌ DLL加载失败（可能位数不匹配或驱动未安装）')
            self._dd_status.setStyleSheet('color:#d94141;')

    def get_dd_dll_path(self) -> str:
        return self._dd_path_edit.text().strip()

    # ── Interception tab ─────────────────────────────────────────────
    def _build_interception_tab(self) -> QWidget:
        from core.backends.interception_backend import InterceptionBackend
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        info = QLabel(
            '<b>Interception</b> 是开源内核驱动，支持按扫描码发送输入，<br>'
            '兼容性广，适合 <b>外服游戏及需要严格穿透的场景</b>。<br><br>'
            '安装步骤：<ol>'
            '<li>pip install pyinterception</li>'
            '<li>以 <b>管理员</b> 身份运行：<br>'
            '<code>install-interception.exe /install</code></li>'
            '<li>重启电脑</li>'
            '</ol>'
            '⚠️ 可能需要开启 <b>测试签名模式</b> 或禁用驱动强制签名。'
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(info)
        lay.addSpacing(8)

        check_btn = QPushButton('检测 Interception 驱动')
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
            self._int_status.setText(
                '❌ 驱动未就绪\n' + InterceptionBackend.unavailable_reason())
            self._int_status.setStyleSheet('color:#d94141;')
