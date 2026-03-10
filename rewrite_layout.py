import re

with open('gui/main_window.py', 'r', encoding='utf-8') as f:
    code = f.read()

NEW_BUILDERS = '''    # ══════════════════════════════════════════════════════════════
    #  UI construction
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_main_area(), 1)

    def _build_sidebar(self) -> QFrame:
        side = QFrame()
        side.setObjectName('sidebar')
        side.setFixedWidth(240)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(16, 20, 16, 20)
        lay.setSpacing(16)

        # Logo
        logo = QLabel('⌨  ClaudyKey')
        logo.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        logo.setObjectName('lbl_logo')
        lay.addWidget(logo)
        lay.addSpacing(16)

        # Mode Selector
        mode_lay = QHBoxLayout()
        mode_lay.setSpacing(0)
        self._btn_mode_loop = QPushButton('🔁循环')
        self._btn_mode_cond = QPushButton('🔍条件')
        self._btn_mode_loop.setCheckable(True)
        self._btn_mode_cond.setCheckable(True)
        
        self._btn_mode_loop.setStyleSheet('QPushButton { border-top-right-radius: 0; border-bottom-right-radius: 0; border-right: none; } QPushButton:checked { background: rgba(255,255,255,0.65); color: #c94080; border-color: rgba(255,255,255,0.6); }')
        self._btn_mode_cond.setStyleSheet('QPushButton { border-top-left-radius: 0; border-bottom-left-radius: 0; } QPushButton:checked { background: rgba(255,255,255,0.65); color: #c94080; border-color: rgba(255,255,255,0.6); }')
        
        self._btn_mode_loop.clicked.connect(lambda: self._set_mode('loop'))
        self._btn_mode_cond.clicked.connect(lambda: self._set_mode('conditional'))
        mode_lay.addWidget(self._btn_mode_loop)
        mode_lay.addWidget(self._btn_mode_cond)
        
        # Wrapped mode lay in group
        frm_mode = QFrame()
        frm_mode.setObjectName('sidebar_group')
        ll = QVBoxLayout(frm_mode)
        ll.setContentsMargins(0,0,0,0)
        mode_lbl = QLabel('运行模式')
        mode_lbl.setObjectName('lbl_sidebar_hdr')
        ll.addWidget(mode_lbl)
        ll.addLayout(mode_lay)
        lay.addWidget(frm_mode)

        # Settings
        frm_set = QFrame()
        frm_set.setObjectName('sidebar_group')
        sl = QVBoxLayout(frm_set)
        sl.setContentsMargins(0,0,0,0)
        
        # Hotkey
        sl.addWidget(QLabel('全局热键', objectName='lbl_sidebar_hdr'))
        self._hotkey_btn = QPushButton('设置: F9')
        self._hotkey_btn.clicked.connect(self._on_hotkey_setup)
        sl.addWidget(self._hotkey_btn)
        sl.addSpacing(8)

        # Input driver
        bd_row = QHBoxLayout()
        bd_row.setContentsMargins(0,0,0,0)
        sl.addWidget(QLabel('输入驱动', objectName='lbl_sidebar_hdr'))
        self._backend_combo = QComboBox()
        self._populate_backend_combo()
        self._backend_combo.currentIndexChanged.connect(self._on_backend_changed)
        bd_cfg_btn = QPushButton('⚙')
        bd_cfg_btn.setFixedWidth(30)
        bd_cfg_btn.clicked.connect(self._on_backend_settings)
        bd_row.addWidget(self._backend_combo, 1)
        bd_row.addWidget(bd_cfg_btn)
        sl.addLayout(bd_row)
        lay.addWidget(frm_set)
        
        lay.addSpacing(16)

        # Navigation Menu
        nav_lbl = QLabel('工作区')
        nav_lbl.setObjectName('lbl_sidebar_hdr')
        lay.addWidget(nav_lbl)
        
        self._btn_nav_macro = QPushButton('📦  宏管理')
        self._btn_nav_macro.setObjectName('btn_nav')
        self._btn_nav_macro.setCheckable(True)
        self._btn_nav_macro.setChecked(True)
        self._btn_nav_macro.clicked.connect(lambda: self._switch_nav(0))
        
        self._btn_nav_trig = QPushButton('⚡  条件触发器')
        self._btn_nav_trig.setObjectName('btn_nav')
        self._btn_nav_trig.setCheckable(True)
        self._btn_nav_trig.clicked.connect(lambda: self._switch_nav(1))
        
        lay.addWidget(self._btn_nav_macro)
        lay.addWidget(self._btn_nav_trig)

        lay.addStretch()

        # File Config
        file_lay = QHBoxLayout()
        file_lay.setContentsMargins(0,0,0,0)
        file_lay.setSpacing(4)
        for label, tip, slot in [('📂', '打开项目', self._open_project), ('💾', '保存项目', self._save_project), ('📄', '新建项目', self._new_project)]:
            b = QPushButton(label)
            b.setToolTip(tip)
            b.setObjectName('btn_icon')
            b.setFixedWidth(32)
            b.clicked.connect(slot)
            file_lay.addWidget(b)
        lay.addLayout(file_lay)
        lay.addSpacing(12)

        # Control area
        self._btn_run = QPushButton('▶ 启动')
        self._btn_run.setObjectName('btn_run')
        self._btn_run.clicked.connect(self._start_all)

        self._btn_stop = QPushButton('■ 停止')
        self._btn_stop.setObjectName('btn_stop')
        self._btn_stop.clicked.connect(self._stop_all)
        self._btn_stop.setEnabled(False)

        lay.addWidget(self._btn_run)
        lay.addWidget(self._btn_stop)

        return side

    def _switch_nav(self, idx: int):
        self.stack.setCurrentIndex(idx)
        self._btn_nav_macro.setChecked(idx == 0)
        self._btn_nav_trig.setChecked(idx == 1)

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
        m_lay.setContentsMargins(0,0,0,0)
        
        m_list_cont = QFrame()
        m_list_cont.setObjectName('glass_card')
        m_list_cont.setFixedWidth(240)
        ml_lay = QVBoxLayout(m_list_cont)
        ml_lay.setContentsMargins(10, 10, 10, 10)
        
        m_hdr = QHBoxLayout()
        ml_lbl = QLabel('宏列表')
        ml_lbl.setObjectName('lbl_section')
        m_add = QPushButton('＋', objectName='btn_icon')
        m_add.setFixedSize(24, 24)
        m_add.clicked.connect(self._new_macro)
        m_del = QPushButton('－', objectName='btn_icon')
        m_del.setFixedSize(24, 24)
        m_del.clicked.connect(self._delete_macro)
        m_hdr.addWidget(ml_lbl, 1)
        m_hdr.addWidget(m_add)
        m_hdr.addWidget(m_del)
        ml_lay.addLayout(m_hdr)

        self.macro_list = QListWidget()
        self.macro_list.currentRowChanged.connect(self._on_macro_selected)
        ml_lay.addWidget(self.macro_list, 1)
        
        m_lay.addWidget(m_list_cont)
        
        self.macro_editor = MacroEditorPanel()
        self.macro_editor.changed.connect(self._on_project_changed)
        m_lay.addWidget(self.macro_editor, 1)

        # Page 1: Trigger Workspace
        trig_page = QWidget()
        t_lay = QHBoxLayout(trig_page)
        t_lay.setContentsMargins(0,0,0,0)

        t_list_cont = QFrame()
        t_list_cont.setObjectName('glass_card')
        t_list_cont.setFixedWidth(240)
        tl_lay = QVBoxLayout(t_list_cont)
        tl_lay.setContentsMargins(10, 10, 10, 10)

        t_hdr = QHBoxLayout()
        tl_lbl = QLabel('触发器列表')
        tl_lbl.setObjectName('lbl_section')
        t_add = QPushButton('＋', objectName='btn_icon')
        t_add.setFixedSize(24, 24)
        t_add.clicked.connect(self._new_trigger)
        t_del = QPushButton('－', objectName='btn_icon')
        t_del.setFixedSize(24, 24)
        t_del.clicked.connect(self._delete_trigger)
        t_hdr.addWidget(tl_lbl, 1)
        t_hdr.addWidget(t_add)
        t_hdr.addWidget(t_del)
        tl_lay.addLayout(t_hdr)

        self.trigger_list = QListWidget()
        self.trigger_list.currentRowChanged.connect(self._on_trigger_selected)
        tl_lay.addWidget(self.trigger_list, 1)

        t_lay.addWidget(t_list_cont)

        self.trigger_editor = TriggerEditorPanel()
        self.trigger_editor.changed.connect(self._on_project_changed)
        t_lay.addWidget(self.trigger_editor, 1)

        self.stack.addWidget(macro_page)
        self.stack.addWidget(trig_page)
        outer.addWidget(self.stack, 1)

        # Log Panel
        log_panel = QFrame()
        log_panel.setObjectName('glass_card')
        log_panel.setFixedHeight(140)
        log_lay = QVBoxLayout(log_panel)
        log_lay.setContentsMargins(10, 6, 10, 10)
        
        log_hdr = QHBoxLayout()
        log_lbl = QLabel('📜 运行日志', objectName='lbl_section')
        self._btn_clear_log = QPushButton('清空', objectName='btn_icon')
        self._btn_clear_log.setFixedWidth(48)
        self._btn_clear_log.clicked.connect(lambda: self._log_view.clear())
        log_hdr.addWidget(log_lbl, 1)
        log_hdr.addWidget(self._btn_clear_log)
        log_lay.addLayout(log_hdr)

        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setObjectName('log_view')
        log_lay.addWidget(self._log_view)

        # Status Bar integration into Log Panel
        stat_lay = QHBoxLayout()
        self._status_lbl = QLabel('就绪', objectName='lbl_status_ok')
        self._hotkey_lbl = QLabel('全局热键: 未知')
        self._hotkey_lbl.setStyleSheet('color: rgba(60,40,50,0.7); font-size: 11px;')
        self._file_lbl = QLabel('')
        self._file_lbl.setStyleSheet('color: rgba(60,40,50,0.7); font-size: 11px;')
        stat_lay.addWidget(self._status_lbl)
        stat_lay.addStretch()
        stat_lay.addWidget(self._file_lbl)
        stat_lay.addSpacing(12)
        stat_lay.addWidget(self._hotkey_lbl)
        log_lay.addLayout(stat_lay)
        
        outer.addWidget(log_panel)
        return w'''

# Extract top level up to `def _build_ui`
p_start = code.find('    def _build_ui(self):')
# Find where selection handlers begin
p_end = code.find('    #  Sidebar list management')

new_code = code[:p_start] + NEW_BUILDERS + '\n\n' + code[p_end:]

# Fix crud & selection methods
new_code = re.sub(r'        self\.stack\.setCurrentIndex\(1\)', '', new_code)
new_code = re.sub(r'        self\.stack\.setCurrentIndex\(2\)', '', new_code)
new_code = re.sub(r'        self\.stack\.setCurrentIndex\(0\)', '', new_code)

# Ensure drop shadows are added to glass_card and sidebar
# Find end of _build_ui to insert drop shadow magic.
# Actually, better to do shadow purely in QSS? No, QGraphicsDropShadowEffect is standard. Let's add it via theme later.

with open('gui/main_window.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
print('Done replacing UI code.')
