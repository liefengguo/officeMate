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

        layout.addStretch(1)

        self.setLayout(layout)