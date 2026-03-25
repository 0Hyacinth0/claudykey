"""Application Controller & State Management."""
import os
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from pynput import keyboard as pynput_kb
from pynput import mouse as pynput_mouse

from core.macro import MacroProject, MacroSequence
from core.executor import MacroExecutor
from core import input_backend as _ib


class AppState:
    IDLE = 'idle'
    RUNNING = 'running'
    ERROR = 'error'


class AppController(QObject):
    """
    Central controller for ClaudyKey GUI.
    Manages the MacroProject model, execution state, and global hotkeys.
    Emits signals that the View (MainWindow and Panels) will subscribe to.
    """
    state_changed = pyqtSignal(str)          # AppState
    project_loaded = pyqtSignal(object, str) # project, path
    project_saved = pyqtSignal(str)          # path
    
    # Execution signals
    step_changed = pyqtSignal(int)
    macro_done = pyqtSignal()
    macro_error = pyqtSignal(str)
    
    # Global messages
    log_message = pyqtSignal(str, str)       # message, kind ('ok', 'err', 'run', 'info')

    # Hotkey registration signals
    hotkey_registered = pyqtSignal(str)      # display_name
    hotkey_failed = pyqtSignal(str)

    DEFAULT_PROJ = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config', 'macros', 'default.json'
    )

    def __init__(self):
        super().__init__()
        self.project: MacroProject = MacroProject()
        self.current_proj_path: str = ''
        self.state: str = AppState.IDLE
        self.active_macro_idx: int = -1  # Used to track user selection from UI
        
        self._executor: Optional[MacroExecutor] = None
        self._listener_kb = None
        self._listener_mouse = None

    def _set_state(self, new_state: str):
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(new_state)

    def is_running(self) -> bool:
        return self.state == AppState.RUNNING

    # ══════════════════════════════════════════════════════════════
    #  Project File I/O
    # ══════════════════════════════════════════════════════════════
    def init_default_project(self):
        """Load default project or create a new empty one."""
        if os.path.exists(self.DEFAULT_PROJ):
            self.load_project(self.DEFAULT_PROJ)
        else:
            self.current_proj_path = self.DEFAULT_PROJ
            seq = MacroSequence()
            self.project.macros.append(seq)
            self.save_project()
            self.project_loaded.emit(self.project, self.current_proj_path)
            self.register_hotkey()

    def new_project(self, name: str):
        if not name.endswith('.json'):
            name += '.json'
        
        self.save_project()
        self.stop_execution()
        
        self.project = MacroProject()
        path = os.path.join(os.path.dirname(self.DEFAULT_PROJ), name)
        self.current_proj_path = path
        self.save_project()
        self.load_project(path)

    def load_project(self, path: str):
        """Load project from path and emit signals."""
        try:
            self.project = MacroProject.load(path)
            self.current_proj_path = path
            
            # Apply saved input backend if exists
            backend = getattr(self.project, 'input_backend', 'dd')
            try:
                _ib.set_backend(backend)
            except Exception:
                _ib.set_backend('dd')
            
            self.register_hotkey()
            self.project_loaded.emit(self.project, path)
            self.log_message.emit('项目已加载', 'ok')
        except Exception as e:
            self.log_message.emit(f'加载失败: {e}', 'err')

    def save_project(self):
        """Save project to current path."""
        p = self.current_proj_path or self.DEFAULT_PROJ
        os.makedirs(os.path.dirname(p), exist_ok=True)
        self.project.save(p)
        self.current_proj_path = p
        self.project_saved.emit(p)
        self.log_message.emit('已保存配置', 'ok')

    def switch_input_backend(self, backend_name: str):
        try:
            _ib.set_backend(backend_name)
            self.project.input_backend = backend_name
            self.save_project()
            self.log_message.emit(f'输入驱动切换 → {backend_name}', 'info')
        except Exception as e:
            self.log_message.emit(f'切换驱动失败: {e}', 'err')

    # ══════════════════════════════════════════════════════════════
    #  Execution Control
    # ══════════════════════════════════════════════════════════════
    def get_selected_sequence(self) -> Optional[MacroSequence]:
        if 0 <= self.active_macro_idx < len(self.project.macros):
            return self.project.macros[self.active_macro_idx]
        elif self.project.macros:
            return self.project.macros[0]
        return None

    def run_macro(self, sequence: Optional[MacroSequence] = None):
        if self.is_running():
            return
            
        if not sequence:
            sequence = self.get_selected_sequence()
        
        if not sequence:
            self.log_message.emit('没有要运行的宏', 'err')
            return

        self.save_project()
        self._set_state(AppState.RUNNING)
        self.log_message.emit(f'开始运行: {sequence.name}', 'run')

        if self._executor and self._executor.is_alive():
            self._executor.stop()

        def done_handler():
            self._on_macro_done()
            
        def err_handler(e):
            self._on_macro_error(e)

        self._executor = MacroExecutor(
            sequence,
            project=self.project,
            on_step=lambda i: self.step_changed.emit(i),
            on_done=done_handler,
            on_error=err_handler,
        )
        self._executor.start()

    def stop_execution(self):
        if self._executor:
            self._executor.stop()
            self._executor = None
        self.log_message.emit('已停止', 'ok')
        self._set_state(AppState.IDLE)
        self.macro_done.emit() # Clean up highlights etc.

    def _on_macro_done(self):
        if self.is_running():
            self.log_message.emit('宏执行完毕', 'ok')
        self._set_state(AppState.IDLE)
        self.macro_done.emit()

    def _on_macro_error(self, msg: str):
        self.log_message.emit(f'错误: {msg}', 'err')
        self._set_state(AppState.ERROR)
        if self._executor:
            self._executor.stop()
            self._executor = None
        self.macro_done.emit()

    # ══════════════════════════════════════════════════════════════
    #  Global Hotkeys
    # ══════════════════════════════════════════════════════════════
    def set_hotkey(self, key_str: str):
        self.project.hotkey = key_str
        self.register_hotkey()
        self.save_project()

    def register_hotkey(self):
        if self._listener_kb:
            self._listener_kb.stop()
            self._listener_kb = None
        if self._listener_mouse:
            self._listener_mouse.stop()
            self._listener_mouse = None

        def toggle():
            if self.is_running():
                # Emit a fast stop
                self.step_changed.emit(-1)
                self.stop_execution()
            else:
                self.run_macro(None)

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

            display = key_conf.replace('key:', '').replace('mouse:', 'Mouse ').upper().strip('<>')
            self.hotkey_registered.emit(display)
            
        except Exception as e:
            self.hotkey_failed.emit(str(e))
            self.log_message.emit(f"热键绑定失败: {e}", "err")

    def cleanup(self):
        """Cleanup before application exit."""
        self.stop_execution()
        self.save_project()
