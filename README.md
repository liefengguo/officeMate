# OfficeMate

OfficeMate 是一款基于 Python 和 PySide6 的桌面文档助手，用于创建快照、比较差异并管理历史版本。

## 主要特性

- **快照管理**：快速为文档建立快照，保存文件路径和时间等信息。
- **历史列表**：查看所有历史快照，按时间排序，可查看或删除。
- **对比功能**：支持 .txt 与 .docx 文档，展示行级或段落级差异。
- **恢复与撤销**：可从指定快照恢复文件，并自动备份上一版本以便撤销。
- **多语言界面**：内置中文、English、Español、Português、日语、Deutsch、Français、Русский、한국어等语言。
- **主题切换**：支持深色、浅色及跟随系统的主题设置。
- **数据目录**：快照存放在平台推荐的个人数据目录（如 Application Support、%APPDATA%、~/.local/share）。
- **配置路径**：应用设置将保存为 INI 文件，路径与快照数据相同：
  - Windows：`%APPDATA%\OfficeMate\OfficeMate.ini`
  - macOS：`~/Library/Application Support/OfficeMate/OfficeMate.ini`
  - Linux：`~/.local/share/OfficeMate/OfficeMate.ini`
- **图形界面**：包含主页、项目页、历史页、对比页与设置页，操作简单。

## 安装与启动

1. 安装 Python 3.10+ 及依赖：
   ```bash
   pip install PySide6 python-docx
   ```
2. 运行应用：
   ```bash
   python main.py
   ```

## 项目结构

- `main.py` – 程序入口
- `app/` – 各界面与 UI 组件
- `core/` – 快照管理、差异算法和数据存储
- `assets/` – 图标与 QSS 样式
- `doc/` – 详细文档

更多信息参见 `doc/OfficeMate.md`。

## 支持语言

- 中文
- English
- Español
- Português
- 日本語
- Deutsch
- Français
- Русский
- 한국어
