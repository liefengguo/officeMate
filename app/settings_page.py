from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QTabWidget,
)
from PyQt5.QtCore import QSettings
from core.themes import apply_theme, load_theme_pref, save_theme_pref

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        title = QLabel("⚙ 软件设置")
        title.setProperty("class", "h2")
        layout.addWidget(title)

        self.settings = QSettings()

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._init_general_tab()
        self._init_appearance_tab()
        self._init_snapshot_tab()
        self._init_diff_tab()

        layout.addStretch(1)
        self.setLayout(layout)

    # ------------------------------------------------------- tab builders
    def _init_general_tab(self):
        widget = QWidget()
        box = QVBoxLayout(widget)

        chk_update = QCheckBox("启动时自动检查更新")
        chk_update.setChecked(self.settings.value("options/auto_update", True, type=bool))
        chk_update.toggled.connect(lambda v: self.settings.setValue("options/auto_update", v))
        box.addWidget(chk_update)

        chk_exp = QCheckBox("启用实验功能")
        chk_exp.setChecked(self.settings.value("options/experimental", False, type=bool))
        chk_exp.toggled.connect(lambda v: self.settings.setValue("options/experimental", v))
        box.addWidget(chk_exp)

        box.addStretch(1)
        self.tabs.addTab(widget, "常规")

    def _init_appearance_tab(self):
        widget = QWidget()
        box = QVBoxLayout(widget)

        theme_auto = QRadioButton("跟随系统")
        theme_light = QRadioButton("浅色")
        theme_dark = QRadioButton("深色")

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
        self.tabs.addTab(widget, "外观")

    def _init_snapshot_tab(self):
        widget = QWidget()
        box = QVBoxLayout(widget)

        chk_auto_compare = QCheckBox("快照便捷对比")
        chk_auto_compare.setChecked(self.settings.value("options/auto_snapshot_compare", False, type=bool))
        chk_auto_compare.toggled.connect(lambda v: self.settings.setValue("options/auto_snapshot_compare", v))
        box.addWidget(chk_auto_compare)

        box.addStretch(1)
        self.tabs.addTab(widget, "快照")

    def _init_diff_tab(self):
        widget = QWidget()
        box = QVBoxLayout(widget)

        options = [
            ("diff/detect_bold", "检测粗体变化"),
            ("diff/detect_italic", "检测斜体变化"),
            ("diff/detect_underline", "检测下划线变化"),
            ("diff/detect_font", "检测字体名称差异"),
            ("diff/detect_color", "检测字体颜色差异"),
            ("diff/detect_size", "检测字体大小差异"),
            ("diff/detect_line_spacing", "检测行间距差异"),
            ("diff/detect_alignment", "检测段落对齐方式"),
            ("diff/detect_numbering", "检测段落编号变化"),
            ("diff/detect_images", "检测图片变动"),
            ("diff/detect_tables", "检测表格变动"),
        ]

        for key, label in options:
            chk = QCheckBox(label)
            chk.setChecked(self.settings.value(key, True, type=bool))
            chk.toggled.connect(lambda v, k=key: self.settings.setValue(k, v))
            box.addWidget(chk)

        box.addStretch(1)
        self.tabs.addTab(widget, "差异检测")
