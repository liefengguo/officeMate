from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
)
from PyQt5.QtCore import QSettings
from core.themes import apply_theme, load_theme_pref, save_theme_pref

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        title = QLabel("⚙ 软件设置")
        title.setProperty("class", "h2")
        layout.addWidget(title)

        # ------------------------- 主题选项 -------------------------
        theme_auto = QRadioButton("跟随系统")
        theme_light = QRadioButton("浅色")
        theme_dark = QRadioButton("深色")

        group = QButtonGroup(self)
        for btn in (theme_auto, theme_light, theme_dark):
            group.addButton(btn)
            layout.addWidget(btn)

        pref = load_theme_pref()
        {"auto": theme_auto, "light": theme_light, "dark": theme_dark}[pref if pref in ("auto", "light", "dark") else "auto"].setChecked(True)

        def _apply_theme(button):
            mapping = {theme_auto: "auto", theme_light: "light", theme_dark: "dark"}
            pref = mapping[button]
            save_theme_pref(pref)
            apply_theme(pref=pref)

        group.buttonClicked.connect(_apply_theme)

        # ----------------------- 其它开关示例 -----------------------
        self.settings = QSettings()
        chk_update = QCheckBox("启动时自动检查更新")
        chk_update.setChecked(self.settings.value("options/auto_update", True, type=bool))
        chk_update.toggled.connect(lambda v: self.settings.setValue("options/auto_update", v))
        layout.addWidget(chk_update)

        chk_exp = QCheckBox("启用实验功能")
        chk_exp.setChecked(self.settings.value("options/experimental", False, type=bool))
        chk_exp.toggled.connect(lambda v: self.settings.setValue("options/experimental", v))
        layout.addWidget(chk_exp)

        chk_auto_compare = QCheckBox("快照便捷对比")
        chk_auto_compare.setChecked(self.settings.value("options/auto_snapshot_compare", False, type=bool))
        chk_auto_compare.toggled.connect(lambda v: self.settings.setValue("options/auto_snapshot_compare", v))
        layout.addWidget(chk_auto_compare)

        # -------------------- Diff detection options --------------------
        chk_bold = QCheckBox("检测粗体变化")
        chk_bold.setChecked(self.settings.value("diff/detect_bold", True, type=bool))
        chk_bold.toggled.connect(lambda v: self.settings.setValue("diff/detect_bold", v))
        layout.addWidget(chk_bold)

        chk_italic = QCheckBox("检测斜体变化")
        chk_italic.setChecked(self.settings.value("diff/detect_italic", True, type=bool))
        chk_italic.toggled.connect(lambda v: self.settings.setValue("diff/detect_italic", v))
        layout.addWidget(chk_italic)

        chk_underline = QCheckBox("检测下划线变化")
        chk_underline.setChecked(self.settings.value("diff/detect_underline", True, type=bool))
        chk_underline.toggled.connect(lambda v: self.settings.setValue("diff/detect_underline", v))
        layout.addWidget(chk_underline)

        chk_font = QCheckBox("检测字体名称差异")
        chk_font.setChecked(self.settings.value("diff/detect_font", True, type=bool))
        chk_font.toggled.connect(lambda v: self.settings.setValue("diff/detect_font", v))
        layout.addWidget(chk_font)

        chk_color = QCheckBox("检测字体颜色差异")
        chk_color.setChecked(self.settings.value("diff/detect_color", True, type=bool))
        chk_color.toggled.connect(lambda v: self.settings.setValue("diff/detect_color", v))
        layout.addWidget(chk_color)

        chk_size = QCheckBox("检测字体大小差异")
        chk_size.setChecked(self.settings.value("diff/detect_size", True, type=bool))
        chk_size.toggled.connect(lambda v: self.settings.setValue("diff/detect_size", v))
        layout.addWidget(chk_size)

        chk_ls = QCheckBox("检测行间距差异")
        chk_ls.setChecked(self.settings.value("diff/detect_line_spacing", True, type=bool))
        chk_ls.toggled.connect(lambda v: self.settings.setValue("diff/detect_line_spacing", v))
        layout.addWidget(chk_ls)

        chk_align = QCheckBox("检测段落对齐方式")
        chk_align.setChecked(self.settings.value("diff/detect_alignment", True, type=bool))
        chk_align.toggled.connect(lambda v: self.settings.setValue("diff/detect_alignment", v))
        layout.addWidget(chk_align)

        chk_num = QCheckBox("检测段落编号变化")
        chk_num.setChecked(self.settings.value("diff/detect_numbering", True, type=bool))
        chk_num.toggled.connect(lambda v: self.settings.setValue("diff/detect_numbering", v))
        layout.addWidget(chk_num)

        chk_img = QCheckBox("检测图片变动")
        chk_img.setChecked(self.settings.value("diff/detect_images", True, type=bool))
        chk_img.toggled.connect(lambda v: self.settings.setValue("diff/detect_images", v))
        layout.addWidget(chk_img)

        chk_table = QCheckBox("检测表格变动")
        chk_table.setChecked(self.settings.value("diff/detect_tables", True, type=bool))
        chk_table.toggled.connect(lambda v: self.settings.setValue("diff/detect_tables", v))
        layout.addWidget(chk_table)

        layout.addStretch(1)

        self.setLayout(layout)
