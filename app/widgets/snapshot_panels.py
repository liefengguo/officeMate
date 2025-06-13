"""
snapshot_panels.py
==================
通用面板组件：
    • SnapshotMiddlePanel  – 负责交互控件（备注输入 / 快照列表 / 对比按钮等）
    • SnapshotDisplayPanel – 右侧显示区域，统一承载差异表格或内容预览
"""

from typing import Optional
from PyQt5.QtCore import pyqtSignal
from core.i18n import _
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QListWidget, QListWidgetItem
)
from ui.components import PrimaryButton, FlatButton

class SnapshotMiddlePanel(QWidget):
    """
    左 / 中交互面板
    mode:
        'note'    – 备注输入框 + 创建快照 / 对比按钮
        'list'    – 快照历史列表
        'compare' – 两快照选择 + 对比按钮
    """

    # 对外信号
    snapshotCreated = pyqtSignal(str)                 # 备注
    compareRequested = pyqtSignal()                   # 请求对比（note 模式）
    snapshotSelected = pyqtSignal(str)                # 列表模式：选中一个快照
    pairCompareRequested = pyqtSignal(str, str)       # compare 模式：两个版本

    def __init__(self, mode: str = "note", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.mode = mode
        self._setup_ui()

    # ------------------------------------------------------------------ UI
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        if self.mode == "note":
            self._init_note(layout)
        elif self.mode == "list":
            self._init_list(layout)
        elif self.mode == "compare":
            self._init_compare(layout)
        else:
            layout.addWidget(QLabel(_("未实现的面板模式")))
        layout.addStretch(1)
        self.setLayout(layout)

    # -------------------- note 模式：备注 + 按钮
    def _init_note(self, layout: QVBoxLayout):
        layout.addWidget(QLabel(_("快照备注：")))
        self.remark_edit = QTextEdit()
        self.remark_edit.setProperty("class", "textinput")
        self.remark_edit.setPlaceholderText(_("输入此版本的备注信息…"))
        self.remark_edit.setFixedHeight(80)
        layout.addWidget(self.remark_edit)

        btn_box = QHBoxLayout()
        self.create_btn = PrimaryButton(_("创建快照"))
        self.compare_btn = FlatButton(_("对比当前与最新"))
        print("self.compare_btn----:",self.compare_btn.property("type"))
        btn_box.addWidget(self.create_btn)
        btn_box.addWidget(self.compare_btn)
        layout.addLayout(btn_box)
        # 连接信号
        self.create_btn.clicked.connect(self._emit_create)
        self.compare_btn.clicked.connect(self.compareRequested)

    def _emit_create(self):
        remark = self.remark_edit.toPlainText().strip()
        self.snapshotCreated.emit(remark)

    # -------------------- list 模式：快照历史
    def _init_list(self, layout: QVBoxLayout):
        layout.addWidget(QLabel(_("快照历史：")))
        self.list_widget = QListWidget()
        self.list_widget.setProperty("class", "snapshot-list")
        self.list_widget.itemClicked.connect(
            lambda item: self.snapshotSelected.emit(item.data(256))
        )
        layout.addWidget(self.list_widget)

    def setSnapshotList(self, titles: list[str]):
        """供外部刷新列表"""
        if self.mode != "list":
            return
        self.list_widget.clear()
        for t in titles:
            item = QListWidgetItem(t)
            item.setData(256, t)
            self.list_widget.addItem(item)

    # -------------------- compare 模式：双选 + 对比
    def _init_compare(self, layout: QVBoxLayout):
        layout.addWidget(QLabel(_("选择需要对比的两个快照：")))
        self.first_list = QListWidget()
        self.first_list.setProperty("class", "snapshot-list")
        self.second_list = QListWidget()
        self.second_list.setProperty("class", "snapshot-list")
        lists_box = QHBoxLayout()
        lists_box.addWidget(self.first_list)
        lists_box.addWidget(self.second_list)
        layout.addLayout(lists_box)

        self.compare_btn = PrimaryButton(_("开始对比"))
        layout.addWidget(self.compare_btn)
        self.compare_btn.clicked.connect(self._emit_pair_compare)

    def _emit_pair_compare(self):
        a = self.first_list.currentItem()
        b = self.second_list.currentItem()
        if a and b:
            self.pairCompareRequested.emit(a.data(256), b.data(256))

    # -------------------- 通用辅助
    def clear(self):
        if self.mode == "note":
            self.remark_edit.clear()
        elif self.mode == "list":
            self.list_widget.clear()


class SnapshotDisplayPanel(QWidget):
    """
    右侧显示面板，统一承载差异表格或内容预览
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._curr_widget: Optional[QWidget] = None
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    # ----------------------------------------------------------------- API
    def set_widget(self, widget: QWidget):
        """替换显示区域内容"""
        if self._curr_widget:
            self._layout.removeWidget(self._curr_widget)
            self._curr_widget.setParent(None)

        # wrap in a preview-pane container
        wrapper = QWidget()
        wrapper.setProperty("class", "preview-pane")
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.addWidget(widget)

        self._curr_widget = wrapper
        self._layout.addWidget(wrapper)