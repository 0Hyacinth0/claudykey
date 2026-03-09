"""Main application window for ClaudyKey."""
import os
import uuid
import threading

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QFrame,
    QStackedWidget, QFileDialog, QMessageBox, QSizePolicy,
    QInputDialog, QComboBox, QDialog,
)
from pynput import keyboard as pynput_kb
from pynput import mouse as pynput_mouse

class HotkeySetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置启停快捷键')
        self.setFixedSize(300, 160)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        lay = QVBoxLayout(self)
        self.lbl = QLabel('正在监听...\n\n请按下任意键盘按键或\n除左键外的鼠标按键。')
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet('font-size: 14px; color: #d15c89; font-weight: bold;')
        lay.addWidget(self.lbl)
        
        self.result_key = None
        
        self.kb_listener = pynput_kb.Listener(on_press=self.on_key)
        self.mouse_listener = pynput_mouse.Listener(on_click=self.on_mouse)
        self.kb_listener.start()
        self.mouse_listener.start()

    def on_key(self, key):
        if self.result_key: return
        try:
            char = key.char
            if char:
                self.result_key = f"key:{char.lower()}"
            else:
                self.result_key = f"key:<{key.name}>"
        except AttributeError:
            self.result_key = f"key:<{key.name}>"
        self.accept_from_thread()

    def on_mouse(self, x, y, button, pressed):
        if not pressed or self.result_key: return
        if button == pynput_mouse.Button.left:
            return  # block left click
        self.result_key = f"mouse:{button.name}"
        self.accept_from_thread()

    def accept_from_thread(self):
        self.kb_listener.stop()
        self.mouse_listener.stop()
        QTimer.singleShot(0, self.accept)

    def closeEvent(self, event):
        self.kb_listener.stop()
        self.mouse_listener.stop()
        super().closeEvent(event)

from core.macro import MacroProject, MacroSequence, TriggerConfig
from core.executor import MacroExecutor
from core.trigger import TriggerEngine
from gui.macro_editor import MacroEditorPanel
from gui.trigger_editor import TriggerEditorPanel
from gui.theme import THEME_QSS


# ── Signal bridge: relay background-thread events to GUI thread ──
class _Bridge(QObject):
    step_changed = pyqtSignal(int)
    macro_done = pyqtSignal()
    macro_error = pyqtSignal(str)
    trigger_fired = pyqtSignal(str)   # trigger id


class MainWindow(QMainWindow):
    DEFAULT_PROJ = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config', 'macros', 'default.json')

    def __init__(self):
        super().__init__()
        self.setWindowTitle('ClaudyKey — AI 连点器')
        self.resize(1100, 720)
        self.setStyleSheet(THEME_QSS)

        self.project = MacroProject()
        self._executor: MacroExecutor | None = None
        self._trigger_engine: TriggerEngine | None = None
        self._bridge = _Bridge()
        self._current_proj_path: str = ''
        self._running = False
        self._listener_kb = None
        self._listener_mouse = None

        self._bridge.step_changed.connect(self._on_step)
        self._bridge.macro_done.connect(self._on_macro_done)
        self._bridge.macro_error.connect(self._on_macro_error)
        self._bridge.trigger_fired.connect(self._on_trigger_fired)

        self._build_ui()
        self._register_hotkey()

        # Auto-load default project
        if os.path.exists(self.DEFAULT_PROJ):
            self._load_project(self.DEFAULT_PROJ)
        else:
            self._new_macro()

    # ══════════════════════════════════════════════════════════════
    #  UI construction
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_toolbar())
        root.addWidget(self._build_body(), 1)
        root.addWidget(self._build_statusbar())

    def _build_toolbar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName('toolbar')
        bar.setFixedHeight(52)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(8)

        # Logo
        logo = QLabel('⌨ ClaudyKey')
        logo.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        logo.setStyleSheet('color:#d15c89;')
        lay.addWidget(logo)
        lay.addSpacing(20)

        self._btn_run = QPushButton('▶  运行')
        self._btn_run.setObjectName('btn_run')
        self._btn_run.clicked.connect(self._start_all)

        self._btn_stop = QPushButton('■  停止')
        self._btn_stop.setObjectName('btn_stop')
        self._btn_stop.clicked.connect(self._stop_all)
        self._btn_stop.setEnabled(False)

        lay.addWidget(self._btn_run)
        lay.addWidget(self._btn_stop)
        lay.addSpacing(15)
        
        lay.addWidget(QLabel('⚡ 快捷键:'))
        self._hotkey_btn = QPushButton("设置: F9")
        self._hotkey_btn.setToolTip("点击设置全局启动/停止的热键")
        self._hotkey_btn.clicked.connect(self._on_hotkey_setup)
        self._hotkey_btn.setFixedWidth(120)
        lay.addWidget(self._hotkey_btn)

        lay.addStretch()

        # File buttons
        for label, tip, slot in [
            ('🗁 打开', '打开项目', self._open_project),
            ('💾 保存', '保存项目', self._save_project),
            ('📄 新建', '新建项目', self._new_project),
        ]:
            b = QPushButton(label)
            b.setToolTip(tip)
            b.clicked.connect(slot)
            lay.addWidget(b)

        return bar

    def _build_body(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(4)
        splitter.setStyleSheet('QSplitter::handle{background:rgba(240, 215, 225, 0.6); border-radius: 2px;}')
        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_editor_area())
        splitter.setSizes([240, 860])
        return splitter

    def _build_sidebar(self) -> QFrame:
        side = QFrame()
        side.setObjectName('sidebar')
        side.setFixedWidth(220)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)

        # ── Macro list ──
        macro_hdr = QHBoxLayout()
        lbl = QLabel('宏 MACROS')
        lbl.setObjectName('lbl_section')
        btn_add_macro = QPushButton('＋')
        btn_add_macro.setObjectName('btn_icon')
        btn_add_macro.setFixedSize(24, 24)
        btn_add_macro.setToolTip('新建宏')
        btn_add_macro.clicked.connect(self._new_macro)
        btn_del_macro = QPushButton('－')
        btn_del_macro.setObjectName('btn_icon')
        btn_del_macro.setFixedSize(24, 24)
        btn_del_macro.setToolTip('删除宏')
        btn_del_macro.clicked.connect(self._delete_macro)
        macro_hdr.addWidget(lbl, 1)
        macro_hdr.addWidget(btn_add_macro)
        macro_hdr.addWidget(btn_del_macro)
        lay.addLayout(macro_hdr)

        self.macro_list = QListWidget()
        self.macro_list.setMaximumHeight(220)
        self.macro_list.currentRowChanged.connect(self._on_macro_selected)
        lay.addWidget(self.macro_list)

        # ── Trigger list ──
        trig_hdr = QHBoxLayout()
        lbl2 = QLabel('触发器 TRIGGERS')
        lbl2.setObjectName('lbl_section')
        btn_add_trig = QPushButton('＋')
        btn_add_trig.setObjectName('btn_icon')
        btn_add_trig.setFixedSize(24, 24)
        btn_add_trig.setToolTip('新建触发器')
        btn_add_trig.clicked.connect(self._new_trigger)
        btn_del_trig = QPushButton('－')
        btn_del_trig.setObjectName('btn_icon')
        btn_del_trig.setFixedSize(24, 24)
        btn_del_trig.setToolTip('删除触发器')
        btn_del_trig.clicked.connect(self._delete_trigger)
        trig_hdr.addWidget(lbl2, 1)
        trig_hdr.addWidget(btn_add_trig)
        trig_hdr.addWidget(btn_del_trig)
        lay.addLayout(trig_hdr)

        self.trigger_list = QListWidget()
        self.trigger_list.setMinimumHeight(80)
        self.trigger_list.currentRowChanged.connect(self._on_trigger_selected)
        lay.addWidget(self.trigger_list, 1)

        return side

    def _build_editor_area(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 8, 12, 8)
        self.stack = QStackedWidget()

        # Page 0: placeholder
        placeholder = QLabel('← 从左侧选择宏或触发器')
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet('color:#ab6a84;font-size:16px;font-weight:bold;')
        self.stack.addWidget(placeholder)

        # Page 1: macro editor
        self.macro_editor = MacroEditorPanel()
        self.macro_editor.changed.connect(self._on_project_changed)
        self.stack.addWidget(self.macro_editor)

        # Page 2: trigger editor
        self.trigger_editor = TriggerEditorPanel()
        self.trigger_editor.changed.connect(self._on_project_changed)
        self.stack.addWidget(self.trigger_editor)

        lay.addWidget(self.stack)
        return w

    def _build_statusbar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName('statusbar_frame')
        bar.setFixedHeight(28)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 0, 12, 0)
        self._status_lbl = QLabel('就绪')
        self._status_lbl.setObjectName('lbl_status_ok')
        self._hotkey_lbl = QLabel('全局热键: 未知')
        self._hotkey_lbl.setStyleSheet('color:#9c7b8c;')
        self._file_lbl = QLabel('')
        self._file_lbl.setStyleSheet('color:#9c7b8c;')
        lay.addWidget(self._status_lbl)
        lay.addStretch()
        lay.addWidget(self._file_lbl)
        lay.addWidget(self._hotkey_lbl)
        return bar

    # ══════════════════════════════════════════════════════════════
    #  Sidebar list management
    # ══════════════════════════════════════════════════════════════
    def _refresh_macro_list(self):
        self.macro_list.clear()
        for m in self.project.macros:
            item = QListWidgetItem(f'⚡ {m.name}')
            item.setData(Qt.ItemDataRole.UserRole, m.id)
            self.macro_list.addItem(item)

    def _refresh_trigger_list(self):
        self.trigger_list.clear()
        for t in self.project.triggers:
            icon = '🖼' if t.type == 'image' else '📝'
            prefix = '' if t.enabled else '○ '
            item = QListWidgetItem(f'{prefix}{icon} {t.name}')
            item.setData(Qt.ItemDataRole.UserRole, t.id)
            self.trigger_list.addItem(item)

    def _on_macro_selected(self, row: int):
        if row < 0 or row >= len(self.project.macros):
            return
        self.trigger_list.clearSelection()
        seq = self.project.macros[row]
        self.macro_editor.load_sequence(seq)
        self.stack.setCurrentIndex(1)

    def _on_trigger_selected(self, row: int):
        if row < 0 or row >= len(self.project.triggers):
            return
        self.macro_list.clearSelection()
        trig = self.project.triggers[row]
        self.trigger_editor.load_trigger(trig, self.project)
        self.stack.setCurrentIndex(2)

    # ══════════════════════════════════════════════════════════════
    #  Macro / Trigger CRUD
    # ══════════════════════════════════════════════════════════════
    def _new_macro(self):
        seq = MacroSequence()
        self.project.macros.append(seq)
        self._refresh_macro_list()
        self.macro_list.setCurrentRow(len(self.project.macros) - 1)

    def _delete_macro(self):
        row = self.macro_list.currentRow()
        if row < 0 or row >= len(self.project.macros):
            return
        self.project.macros.pop(row)
        self._refresh_macro_list()
        self.stack.setCurrentIndex(0)

    def _new_trigger(self):
        t = TriggerConfig()
        self.project.triggers.append(t)
        self._refresh_trigger_list()
        self.trigger_list.setCurrentRow(len(self.project.triggers) - 1)

    def _delete_trigger(self):
        row = self.trigger_list.currentRow()
        if row < 0 or row >= len(self.project.triggers):
            return
        self.project.triggers.pop(row)
        self._refresh_trigger_list()
        self.stack.setCurrentIndex(0)

    # ══════════════════════════════════════════════════════════════
    #  Project file I/O
    # ══════════════════════════════════════════════════════════════
    def _on_project_changed(self):
        self._refresh_macro_list()
        self._refresh_trigger_list()
        # Re-refresh trigger editor macro options
        if self.stack.currentIndex() == 2:
            self.trigger_editor._refresh_macro_combo()

    def _new_project(self):
        self._stop_all()
        self.project = MacroProject()
        self._current_proj_path = ''
        self._refresh_macro_list()
        self._refresh_trigger_list()
        self.stack.setCurrentIndex(0)
        self._file_lbl.setText('')
        self._register_hotkey()
        self._new_macro()

    def _save_project(self):
        if not self._current_proj_path:
            path, _ = QFileDialog.getSaveFileName(
                self, '保存项目', self.DEFAULT_PROJ,
                'ClaudyKey 项目 (*.json);;All Files (*)')
            if not path:
                return
            self._current_proj_path = path
        os.makedirs(os.path.dirname(self._current_proj_path), exist_ok=True)
        self.project.save(self._current_proj_path)
        self._file_lbl.setText(os.path.basename(self._current_proj_path))
        self._set_status('已保存', 'ok')

    def _open_project(self):
        self._stop_all()
        path, _ = QFileDialog.getOpenFileName(
            self, '打开项目', '',
            'ClaudyKey 项目 (*.json);;All Files (*)')
        if path:
            self._load_project(path)

    def _load_project(self, path: str):
        try:
            self.project = MacroProject.load(path)
            self._current_proj_path = path
            self._refresh_macro_list()
            self._refresh_trigger_list()
            self.stack.setCurrentIndex(0)
            self._file_lbl.setText(os.path.basename(path))
            self._register_hotkey()
            self._set_status('项目已加载', 'ok')
        except Exception as e:
            QMessageBox.critical(self, '加载失败', str(e))

    # ══════════════════════════════════════════════════════════════
    #  Run / Stop
    # ══════════════════════════════════════════════════════════════
    def _start_all(self):
        if self._running:
            return
        if not self.project.macros and not self.project.triggers:
            self._set_status('没有宏或触发器', 'err')
            return
        self._running = True
        self._btn_run.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._set_status('运行中…', 'run')

        # Start trigger engine (if any enabled triggers)
        enabled = [t for t in self.project.triggers if t.enabled]
        if enabled:
            self._trigger_engine = TriggerEngine(
                enabled, self._on_trigger_fired_bg)
            self._trigger_engine.start()

        # Run first macro (simple mode — run selected macro)
        row = self.macro_list.currentRow()
        if 0 <= row < len(self.project.macros):
            self._run_macro(self.project.macros[row])

    def _run_macro(self, seq):
        if self._executor and self._executor.is_alive():
            self._executor.stop()
        self._executor = MacroExecutor(
            seq,
            on_step=lambda i: self._bridge.step_changed.emit(i),
            on_done=lambda: self._bridge.macro_done.emit(),
            on_error=lambda e: self._bridge.macro_error.emit(e),
        )
        self._executor.start()

    def _stop_all(self):
        if self._executor:
            self._executor.stop()
            self._executor = None
        if self._trigger_engine:
            self._trigger_engine.stop()
            self._trigger_engine = None
        self._running = False
        self._btn_run.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self.macro_editor.clear_highlight()
        self._set_status('已停止', 'ok')

    # ══════════════════════════════════════════════════════════════
    #  Callbacks from background threads (via _bridge)
    # ══════════════════════════════════════════════════════════════
    def _on_step(self, idx: int):
        self.macro_editor.highlight_step(idx)

    def _on_macro_done(self):
        if self._running:
            self._set_status('宏执行完毕', 'ok')
        self._running = False
        self._btn_run.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self.macro_editor.clear_highlight()

    def _on_macro_error(self, msg: str):
        self._set_status(f'错误: {msg}', 'err')
        self._stop_all()

    def _on_trigger_fired_bg(self, trigger: TriggerConfig):
        """Called from TriggerEngine thread."""
        self._bridge.trigger_fired.emit(trigger.id)
        # Execute the action on this thread (non-GUI)
        self._execute_trigger_action(trigger)

    def _on_trigger_fired(self, tid: str):
        """Called on GUI thread via bridge."""
        trig = next((t for t in self.project.triggers if t.id == tid), None)
        if trig:
            self._set_status(f'触发: {trig.name}', 'run')

    def _execute_trigger_action(self, trigger: TriggerConfig):
        """Execute the trigger's configured action (called from background thread)."""
        if trigger.action_type == 'run_macro':
            mid = trigger.action_params.get('macro_id', '')
            seq = next((m for m in self.project.macros if m.id == mid), None)
            if seq:
                self._run_macro(seq)
        elif trigger.action_type == 'click':
            from pynput.mouse import Controller as MC, Button
            mc = MC()
            x = trigger.action_params.get('x', 0)
            y = trigger.action_params.get('y', 0)
            mc.position = (x, y)
            mc.click(Button.left)
        elif trigger.action_type == 'key':
            from pynput.keyboard import Controller as KC
            from core.executor import _KEY_MAP
            kc = KC()
            keys = [_KEY_MAP.get(k.strip().lower(), k.strip())
                    for k in trigger.action_params.get('key', '').split('+')]
            for k in keys[:-1]:
                kc.press(k)
            kc.press(keys[-1])
            kc.release(keys[-1])
            for k in reversed(keys[:-1]):
                kc.release(k)

    # ══════════════════════════════════════════════════════════════
    #  Status bar
    # ══════════════════════════════════════════════════════════════
    def _set_status(self, msg: str, kind: str = 'ok'):
        styles = {
            'ok':  'color:#1fa357;',
            'run': 'color:#d6871a;',
            'err': 'color:#d94141;',
        }
        self._status_lbl.setText(msg)
        self._status_lbl.setStyleSheet(styles.get(kind, ''))

    def _on_hotkey_setup(self):
        dlg = HotkeySetDialog(self)
        if dlg.exec() and dlg.result_key:
            self.project.hotkey = dlg.result_key
            self._register_hotkey()
            self._on_project_changed()

    def _register_hotkey(self):
        if getattr(self, '_listener_kb', None):
            self._listener_kb.stop()
            self._listener_kb = None
        if getattr(self, '_listener_mouse', None):
            self._listener_mouse.stop()
            self._listener_mouse = None

        def toggle():
            if self._running:
                self._bridge.macro_done.emit()  # reuse signal to stop
                self._stop_all()
            else:
                self._start_all()

        key_conf = self.project.hotkey
        if not key_conf.startswith('key:') and not key_conf.startswith('mouse:'):
            key_conf = f"key:<{key_conf.strip('<>')}>"
            self.project.hotkey = key_conf

        try:
            if key_conf.startswith('key:'):
                k = key_conf[4:]
                self._listener_kb = pynput_kb.GlobalHotKeys({k: toggle})
                self._listener_kb.start()
            elif key_conf.startswith('mouse:'):
                m = key_conf[6:]
                def on_click(x, y, button, pressed):
                    if pressed and button.name == m:
                        toggle()
                self._listener_mouse = pynput_mouse.Listener(on_click=on_click)
                self._listener_mouse.start()

            # Update UI labels
            display = key_conf.replace('key:', '').replace('mouse:', 'Mouse ').upper().strip('<>')
            self._btn_run.setText(f'▶  运行  ({display})')
            self._btn_stop.setText(f'■  停止  ({display})')
            self._hotkey_btn.setText(f'设置: {display}')
            self._hotkey_lbl.setText(f'全局热键: {display} 开始 / 停止')
        except Exception as e:
            self._set_status(f"热键绑定失败: {e}", "err")

    # ══════════════════════════════════════════════════════════════
    #  Window close
    # ══════════════════════════════════════════════════════════════
    def closeEvent(self, event):
        self._stop_all()
        self._save_project()
        event.accept()
