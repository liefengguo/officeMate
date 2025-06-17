from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QTabWidget,
)
from PySide6.QtCore import QSettings
from core.i18n import _, get_language, set_language, i18n
from core.themes import apply_theme, load_theme_pref, save_theme_pref

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.title = QLabel(_("⚙ 软件设置"))
        self.title.setProperty("class", "h2")
        layout.addWidget(self.title)

        self.settings = QSettings()

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._init_general_tab()
        self._init_appearance_tab()
        self._init_snapshot_tab()
        self._init_diff_tab()

        layout.addStretch(1)
        self.setLayout(layout)

        i18n.language_changed.connect(self.retranslate_ui)

    # ------------------------------------------------------- i18n
    def retranslate_ui(self):
        self.title.setText(_("⚙ 软件设置"))
        self.tabs.clear()
        self._init_general_tab()
        self._init_appearance_tab()
        self._init_snapshot_tab()
        self._init_diff_tab()

    # ------------------------------------------------------- tab builders
    def _init_general_tab(self):
        widget = QWidget()
        box = QVBoxLayout(widget)

        chk_update = QCheckBox(_("启动时自动检查更新"))
        chk_update.setChecked(self.settings.value("options/auto_update", True, type=bool))
        chk_update.toggled.connect(lambda v: self.settings.setValue("options/auto_update", v))
        box.addWidget(chk_update)

        chk_exp = QCheckBox(_("启用实验功能"))
        chk_exp.setChecked(self.settings.value("options/experimental", False, type=bool))
        chk_exp.toggled.connect(lambda v: self.settings.setValue("options/experimental", v))
        box.addWidget(chk_exp)

        lang_label = QLabel(_("界面语言："))
        box.addWidget(lang_label)
        lang_buttons = {
            "zh": QRadioButton("中文"),
            "en": QRadioButton("English"),
            "es": QRadioButton("Español"),
            "pt": QRadioButton("Português"),
            "ja": QRadioButton("日本語"),
            "de": QRadioButton("Deutsch"),
            "fr": QRadioButton("Français"),
            "ru": QRadioButton("Русский"),
            "ko": QRadioButton("한국어"),
        }
        lang_group = QButtonGroup(self)
        for btn in lang_buttons.values():
            lang_group.addButton(btn)
            box.addWidget(btn)

        current = get_language()
        lang_buttons.get(current, lang_buttons["zh"]).setChecked(True)

        def _apply_lang(button):
            for code, btn in lang_buttons.items():
                if btn is button:
                    set_language(code)
                    break

        lang_group.buttonClicked.connect(_apply_lang)

        box.addStretch(1)
        self.tabs.addTab(widget, _("常规"))

    def _init_appearance_tab(self):
        widget = QWidget()
        box = QVBoxLayout(widget)

        theme_auto = QRadioButton(_("跟随系统"))
        theme_light = QRadioButton(_("浅色"))
        theme_dark = QRadioButton(_("深色"))

        group = QButtonGroup(self)
        for btn in (theme_auto, theme_light, theme_dark):
            group.addButton(btn)
            box.addWidget(btn)

        pref = load_theme_pref()
        {"auto": theme_auto, "light": theme_light, "dark": theme_dark}.get(pref, theme_auto).setChecked(True)

        def _apply_theme(button):
            mapping = {theme_auto: "auto", theme_light: "light", theme_dark: "dark"}
            pref = mapping[button]
            save_theme_pref(pref)
            apply_theme(pref=pref)

        group.buttonClicked.connect(_apply_theme)

        box.addStretch(1)
        self.tabs.addTab(widget, _("外观"))

    def _init_snapshot_tab(self):
        widget = QWidget()
        box = QVBoxLayout(widget)

        chk_auto_compare = QCheckBox(_("快照便捷对比"))
        chk_auto_compare.setChecked(self.settings.value("options/auto_snapshot_compare", False, type=bool))
        chk_auto_compare.toggled.connect(lambda v: self.settings.setValue("options/auto_snapshot_compare", v))
        box.addWidget(chk_auto_compare)

        chk_compact = QCheckBox(_("简洁显示"))
        chk_compact.setChecked(self.settings.value("diff/compact_style", False, type=bool))
        chk_compact.toggled.connect(lambda v: self.settings.setValue("diff/compact_style", v))
        box.addWidget(chk_compact)

        box.addStretch(1)
        self.tabs.addTab(widget, _("快照"))

    def _init_diff_tab(self):
        widget = QWidget()
        box = QVBoxLayout(widget)

        self._diff_checks = []

        chk_all = QCheckBox(_("全选"))
        box.addWidget(chk_all)

        options = [
            ("diff/detect_bold", _("检测粗体变化")),
            ("diff/detect_italic", _("检测斜体变化")),
            ("diff/detect_underline", _("检测下划线变化")),
            ("diff/detect_font", _("检测字体名称差异")),
            ("diff/detect_color", _("检测字体颜色差异")),
            ("diff/detect_size", _("检测字体大小差异")),
            ("diff/detect_line_spacing", _("检测行间距差异")),
            ("diff/detect_alignment", _("检测段落对齐方式")),
            ("diff/detect_style", _("检测段落样式变化")),
            ("diff/detect_indent", _("检测段落缩进变化")),
            ("diff/detect_numbering", _("检测段落编号变化")),
            ("diff/detect_images", _("检测图片变动")),
            ("diff/detect_tables", _("检测表格变动")),
        ]

        for key, label in options:
            chk = QCheckBox(label)
            chk.setChecked(self.settings.value(key, True, type=bool))
            chk.toggled.connect(lambda v, k=key: self.settings.setValue(k, v))
            box.addWidget(chk)
            self._diff_checks.append(chk)

        def _update_all_state():
            all_checked = all(c.isChecked() for c in self._diff_checks)
            chk_all.blockSignals(True)
            chk_all.setChecked(all_checked)
            chk_all.blockSignals(False)

        def _set_all(checked: bool):
            for chk in self._diff_checks:
                chk.setChecked(checked)

        chk_all.toggled.connect(_set_all)
        for chk in self._diff_checks:
            chk.toggled.connect(_update_all_state)
        _update_all_state()

        box.addStretch(1)
        self.tabs.addTab(widget, _("差异检测"))
