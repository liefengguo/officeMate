from PyQt5.QtCore import QSettings, pyqtSignal, QObject

# Mapping of original Chinese texts to translations
_TRANSLATIONS = {
    "DocSnap 文档助手": {"en": "DocSnap Assistant"},
    "DocSnap 文档管理主页": {"en": "DocSnap Dashboard"},
    "📂 已添加文档列表": {"en": "📂 Added Documents"},
    "➕ 添加项目": {"en": "➕ Add Project"},
    "暂无文档，点击上方按钮添加": {"en": "No documents yet, click the button above to add"},
    "选择文档": {"en": "Select Document"},
    "文档 (*.txt *.docx);;所有文件 (*)": {"en": "Documents (*.txt *.docx);;All files (*)"},
    "文件不存在": {"en": "File not found"},
    "该文件无法访问：\n{path}": {"en": "Cannot access file:\n{path}"},
    "无法访问：{path}": {"en": "Cannot access: {path}"},
    "快照历史": {"en": "Snapshot History"},
    "← 返回主页": {"en": "\u2190 Back"},
    "文档：{name}": {"en": "Document: {name}"},
    "对比选中快照": {"en": "Compare Selected"},
    "查看快照内容": {"en": "View Snapshot"},
    "暂无快照记录": {"en": "No snapshots"},
    "未知时间": {"en": "Unknown"},
    "提示": {"en": "Notice"},
    "选择错误": {"en": "Selection Error"},
    "请选择两个快照进行对比": {"en": "Please select two snapshots to compare"},
    "请至少选择一个快照进行预览": {"en": "Please select at least one snapshot to preview"},
    "快照差异对比": {"en": "Snapshot Diff"},
    "成功": {"en": "Success"},
    "快照已创建！\n时间：{timestamp}": {"en": "Snapshot created!\nTime: {timestamp}"},
    "错误": {"en": "Error"},
    "创建快照失败：{e}": {"en": "Failed to create snapshot: {e}"},
    "⚠️ 没有可用快照进行对比": {"en": "No snapshot available for comparison"},
    "历史对比": {"en": "History"},
    "最新文档": {"en": "Latest"},
    "当前文档与最新快照没有任何差异。": {"en": "No difference between current file and latest snapshot."},
    "对比失败：{e}": {"en": "Comparison failed: {e}"},
    "👉 在左侧填写备注并点击“创建快照”": {"en": "\uD83D\uDC49 Enter remarks on the left then click 'Create Snapshot'"},
    "✅ 快照已创建！": {"en": "\u2705 Snapshot created!"},
    "📜 {name} 的快照历史": {"en": "📜 Snapshot history of {name}"},
    "删除所选快照": {"en": "Delete Selected"},
    "恢复所选快照": {"en": "Restore Selected"},
    "👉 选择快照查看内容或恢复": {"en": "\uD83D\uDC49 Select a snapshot to view or restore"},
    "确定删除该快照？": {"en": "Delete this snapshot?"},
    "✂️ 已删除快照": {"en": "Snapshot deleted"},
    "无法读取快照内容：{e}": {"en": "Unable to load snapshot: {e}"},
    "对比当前与最新": {"en": "Compare with Latest"},
    "开始对比": {"en": "Compare"},
    "未实现的面板模式": {"en": "Panel mode not implemented"},
    "快照备注：": {"en": "Snapshot note:"},
    "输入此版本的备注信息…": {"en": "Enter notes for this version…"},
    "创建快照": {"en": "Create Snapshot"},
    "快照历史：": {"en": "Snapshot history:"},
    "选择需要对比的两个快照：": {"en": "Select two snapshots to compare:"},
    "开始对比": {"en": "Compare"},
    "📭 没有快照可用": {"en": "No snapshots available"},
    "👉 请选择两个快照后点击“对比”": {"en": "Select two snapshots then click 'Compare'"},
    "两个快照无差异。": {"en": "No differences between snapshots."},
    "删除快照": {"en": "Delete Snapshot"},
    "加载内容失败：{e}": {"en": "Failed to load content: {e}"},
    "差异结果将在这里显示...": {"en": "Diff results will appear here..."},
    "没有检测到差异。": {"en": "No differences detected."},
    "快照内容预览": {"en": "Snapshot Preview"},
    "主题(&T)": {"en": "Theme(&T)"},
    "跟随系统": {"en": "System"},
    "浅色": {"en": "Light"},
    "深色": {"en": "Dark"},
    "对比选中的两个快照": {"en": "Compare Selected Snapshots"},
    "⚙ 软件设置": {"en": "⚙ Settings"},
    "启动时自动检查更新": {"en": "Check for updates on startup"},
    "启用实验功能": {"en": "Enable experimental features"},
    "界面语言：": {"en": "Language:"},
    "常规": {"en": "General"},
    "外观": {"en": "Appearance"},
    "快照便捷对比": {"en": "Quick snapshot compare"},
    "快照": {"en": "Snapshots"},
    "差异检测": {"en": "Diff Options"},
    "检测粗体变化": {"en": "Detect bold changes"},
    "检测斜体变化": {"en": "Detect italic changes"},
    "检测下划线变化": {"en": "Detect underline changes"},
    "检测字体名称差异": {"en": "Detect font name changes"},
    "检测字体颜色差异": {"en": "Detect font color changes"},
    "检测字体大小差异": {"en": "Detect font size changes"},
    "检测行间距差异": {"en": "Detect line spacing changes"},
    "检测段落对齐方式": {"en": "Detect paragraph alignment"},
    "检测段落编号变化": {"en": "Detect numbering changes"},
    "检测图片变动": {"en": "Detect image changes"},
    "检测表格变动": {"en": "Detect table changes"}
}

class _I18N(QObject):
    language_changed = pyqtSignal()


i18n = _I18N()

_current_lang = None


def get_language() -> str:
    global _current_lang
    if _current_lang is None:
        _current_lang = QSettings().value("ui/language", "zh")
    return _current_lang


def set_language(lang: str) -> None:
    global _current_lang
    if lang == _current_lang:
        return
    _current_lang = lang
    QSettings().setValue("ui/language", lang)
    i18n.language_changed.emit()


def _(text: str) -> str:
    lang = get_language()
    trans = _TRANSLATIONS.get(text, {})
    return trans.get(lang, text)
