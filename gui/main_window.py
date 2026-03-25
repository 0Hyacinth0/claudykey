"""Main application window for ClaudyKey."""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QFrame,
    QStackedWidget,
)

from core.macro import MacroProject, MacroSequence, TriggerConfig
from gui.macro_editor import MacroEditorPanel
from gui.trigger_editor import TriggerEditorPanel
from gui.theme import THEME_QSS

from gui.controller import AppController
from gui.panels import SidebarPanel, LogPanel


class MainWindow(QMainWindow):
    """Refactored main window mapping MVC Controller and Sub-Panels."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ClaudyKey')
        self.resize(1100, 720)
        self.setStyleSheet(THEME_QSS)

        # MVC: Initialize Controller
        self.controller = AppController()
        
        self._build_ui()
        self._bind_controller()

        # Connect internal panel signals
        self.macro_editor.changed.connect(self._on_project_changed)
        self.trigger_editor.changed.connect(self._on_project_changed)
        self.sidebar.nav_changed.connect(self._switch_nav)

        # Let the controller decide the initial project state
        self.controller.init_default_project()

    def _bind_controller(self):
        self.controller.project_loaded.connect(self._on_project_loaded)
        self.controller.step_changed.connect(self._on_step)
        self.controller.macro_done.connect(self._on_macro_done)

    # ══════════════════════════════════════════════════════════════
    #  UI construction
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Phase 3: Modular panels
        self.sidebar = SidebarPanel(self.controller)
        root.addWidget(self.sidebar)

        root.addWidget(self._build_main_area(), 1)

    def _switch_nav(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def _build_main_area(self) -> QWidget:
        w = QFrame()
        w.setObjectName('main_area')
        
        outer = QVBoxLayout(w)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(12)

        self.stack = QStackedWidget()

        # Page 0: Macro Workspace
        macro_page = QWidget()
        m_lay = QHBoxLayout(macro_page)
        m_lay.setContentsMargins(0, 0, 0, 0)
        
        m_list_cont = QFrame()
        m_list_cont.setObjectName('glass_card')
        m_list_cont.setFixedWidth(240)
        ml_lay = QVBoxLayout(m_list_cont)
        ml_lay.setContentsMargins(10, 10, 10, 10)
        
        m_hdr = QHBoxLayout()
        ml_lbl = QLabel('宏列表')
        ml_lbl.setObjectName('lbl_section')
        m_add = QPushButton('＋', objectName='btn_icon')
        m_add.setFixedSize(28, 28)
        m_add.setToolTip('新建宏')
        m_add.clicked.connect(self._new_macro)
        m_del = QPushButton('－', objectName='btn_icon')
        m_del.setFixedSize(28, 28)
        m_del.setToolTip('删除宏')
        m_del.clicked.connect(self._delete_macro)
        m_hdr.addWidget(ml_lbl, 1)
        m_hdr.addWidget(m_add)
        m_hdr.addWidget(m_del)
        ml_lay.addLayout(m_hdr)

        self.macro_list = QListWidget()
        self.macro_list.currentRowChanged.connect(self._on_macro_selected)
        ml_lay.addWidget(self.macro_list, 1)

        self._macro_empty = QLabel('◇\n点击 ＋ 创建第一个宏')
        self._macro_empty.setObjectName('empty_state')
        self._macro_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._macro_empty.setWordWrap(True)
        ml_lay.addWidget(self._macro_empty)
        self._macro_empty.setVisible(False)
        
        m_lay.addWidget(m_list_cont)
        
        self._m_right_stack = QStackedWidget()
        self._macro_editor_empty = QLabel('⊞\n请在左侧选择或创建一个宏以开始编辑')
        self._macro_editor_empty.setObjectName('empty_state')
        self._macro_editor_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._m_right_stack.addWidget(self._macro_editor_empty)
        
        self.macro_editor = MacroEditorPanel()
        self._m_right_stack.addWidget(self.macro_editor)
        m_lay.addWidget(self._m_right_stack, 1)

        # Page 1: Trigger Workspace
        trig_page = QWidget()
        t_lay = QHBoxLayout(trig_page)
        t_lay.setContentsMargins(0, 0, 0, 0)

        t_list_cont = QFrame()
        t_list_cont.setObjectName('glass_card')
        t_list_cont.setFixedWidth(240)
        tl_lay = QVBoxLayout(t_list_cont)
        tl_lay.setContentsMargins(10, 10, 10, 10)

        t_hdr = QHBoxLayout()
        tl_lbl = QLabel('触发器列表')
        tl_lbl.setObjectName('lbl_section')
        t_add = QPushButton('＋', objectName='btn_icon')
        t_add.setFixedSize(28, 28)
        t_add.setToolTip('新建触发器')
        t_add.clicked.connect(self._new_trigger)
        t_del = QPushButton('－', objectName='btn_icon')
        t_del.setFixedSize(28, 28)
        t_del.setToolTip('删除触发器')
        t_del.clicked.connect(self._delete_trigger)
        t_hdr.addWidget(tl_lbl, 1)
        t_hdr.addWidget(t_add)
        t_hdr.addWidget(t_del)
        tl_lay.addLayout(t_hdr)

        self.trigger_list = QListWidget()
        self.trigger_list.currentRowChanged.connect(self._on_trigger_selected)
        tl_lay.addWidget(self.trigger_list, 1)

        self._trigger_empty = QLabel('⯌\n点击 ＋ 创建第一个触发器')
        self._trigger_empty.setObjectName('empty_state')
        self._trigger_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._trigger_empty.setWordWrap(True)
        tl_lay.addWidget(self._trigger_empty)
        self._trigger_empty.setVisible(False)

        t_lay.addWidget(t_list_cont)

        self._t_right_stack = QStackedWidget()
        self._trigger_editor_empty = QLabel('⭃\n请在左侧选择或创建一个触发器以开始编辑')
        self._trigger_editor_empty.setObjectName('empty_state')
        self._trigger_editor_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._t_right_stack.addWidget(self._trigger_editor_empty)
        
        self.trigger_editor = TriggerEditorPanel()
        self._t_right_stack.addWidget(self.trigger_editor)
        t_lay.addWidget(self._t_right_stack, 1)

        self.stack.addWidget(macro_page)
        self.stack.addWidget(trig_page)
        outer.addWidget(self.stack, 1)

        # Log Panel
        self.log_panel = LogPanel(self.controller)
        outer.addWidget(self.log_panel)
        return w

    #  Controller Signal Handlers
    # ══════════════════════════════════════════════════════════════
    def _on_project_loaded(self, project: MacroProject, path: str):
        self._refresh_macro_list()
        self._refresh_trigger_list()

    def _on_step(self, idx: int):
        self.macro_editor.highlight_step(idx)

    def _on_macro_done(self):
        self.macro_editor.clear_highlight()

    #  Sidebar list management
    # ══════════════════════════════════════════════════════════════
    def _refresh_macro_list(self):
        old_row = self.macro_list.currentRow()
        self.macro_list.blockSignals(True)
        self.macro_list.clear()
        
        project = self.controller.project
        for m in project.macros:
            item = QListWidgetItem(f'⊞ {m.name}')
            item.setData(Qt.ItemDataRole.UserRole, m.id)
            self.macro_list.addItem(item)
            
        if 0 <= old_row < self.macro_list.count():
            self.macro_list.setCurrentRow(old_row)
        elif self.macro_list.count() > 0:
            self.macro_list.setCurrentRow(0)
            
        self.macro_list.blockSignals(False)
        has_items = self.macro_list.count() > 0
        self.macro_list.setVisible(has_items)
        self._macro_empty.setVisible(not has_items)
        
        self._on_macro_selected(self.macro_list.currentRow())

    def _refresh_trigger_list(self):
        old_row = self.trigger_list.currentRow()
        self.trigger_list.blockSignals(True)
        self.trigger_list.clear()
        
        project = self.controller.project
        for t in project.triggers:
            icon = '⛶' if t.type == 'image' else '≡'
            prefix = '● ' if t.enabled else '○ '
            item = QListWidgetItem(f'{prefix}{icon} {t.name}')
            item.setData(Qt.ItemDataRole.UserRole, t.id)
            self.trigger_list.addItem(item)
            
        if 0 <= old_row < self.trigger_list.count():
            self.trigger_list.setCurrentRow(old_row)
        elif self.trigger_list.count() > 0:
            self.trigger_list.setCurrentRow(0)
            
        self.trigger_list.blockSignals(False)
        has_items = self.trigger_list.count() > 0
        self.trigger_list.setVisible(has_items)
        self._trigger_empty.setVisible(not has_items)
        
        if hasattr(self, 'trigger_editor'):
            self._on_trigger_selected(self.trigger_list.currentRow())

    def _on_macro_selected(self, row: int):
        self.controller.active_macro_idx = row
        if row < 0 or row >= len(self.controller.project.macros):
            self._m_right_stack.setCurrentIndex(0)
            return
        self._m_right_stack.setCurrentIndex(1)
        self.trigger_list.clearSelection()
        seq = self.controller.project.macros[row]
        self.macro_editor.project = self.controller.project
        self.macro_editor.load_sequence(seq)

    def _on_trigger_selected(self, row: int):
        if row < 0 or row >= len(self.controller.project.triggers):
            self._t_right_stack.setCurrentIndex(0)
            return
        self._t_right_stack.setCurrentIndex(1)
        self.macro_list.clearSelection()
        trig = self.controller.project.triggers[row]
        self.trigger_editor.load_trigger(trig, self.controller.project)

    # ══════════════════════════════════════════════════════════════
    #  Macro / Trigger CRUD
    # ══════════════════════════════════════════════════════════════
    def _new_macro(self):
        seq = MacroSequence()
        self.controller.project.macros.append(seq)
        self._refresh_macro_list()
        self.macro_list.setCurrentRow(len(self.controller.project.macros) - 1)

    def _delete_macro(self):
        row = self.macro_list.currentRow()
        if row < 0 or row >= len(self.controller.project.macros):
            return
        self.controller.project.macros.pop(row)
        self._refresh_macro_list()

    def _new_trigger(self):
        t = TriggerConfig()
        self.controller.project.triggers.append(t)
        self._refresh_trigger_list()
        self.trigger_list.setCurrentRow(len(self.controller.project.triggers) - 1)

    def _delete_trigger(self):
        row = self.trigger_list.currentRow()
        if row < 0 or row >= len(self.controller.project.triggers):
            return
        self.controller.project.triggers.pop(row)
        self._refresh_trigger_list()

    def _on_project_changed(self):
        self.controller.save_project()
        self._refresh_macro_list()
        self._refresh_trigger_list()
        if self.stack.currentIndex() == 2:
            self.trigger_editor._refresh_macro_combo()

    def closeEvent(self, event):
        self.controller.cleanup()
        event.accept()
