# core/snapshot.py
import hashlib
import shutil
import os
import datetime
from abc import ABC, abstractmethod
from core.version_db import VersionDB
from docplatform.paths import get_snapshot_dir
from core.utils import get_file_hash


class SnapshotStrategy(ABC):
    """抽象快照策略接口"""

    @abstractmethod
    def supports(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass


class DocxSnapshot(SnapshotStrategy):
    """处理 .docx 文档的快照提取"""

    def supports(self, file_path: str) -> bool:
        return file_path.endswith(".docx")

    def extract_text(self, file_path: str) -> str:
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)


class TxtSnapshot(SnapshotStrategy):
    """处理 .txt 文本的快照提取"""

    def supports(self, file_path: str) -> bool:
        return file_path.endswith(".txt")

    def extract_text(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


class SnapshotManager:
    """快照管理器，协调策略 + 存储 + 元信息"""

    def __init__(self):
        self.strategies = [DocxSnapshot(), TxtSnapshot()]
        self.version_db = VersionDB()

    def create_snapshot(self, file_path: str, remark="") -> dict:
        strategy = self._get_strategy(file_path)
        if not strategy:
            raise ValueError(f"Unsupported file type: {file_path}")

        content = strategy.extract_text(file_path)
        file_hash = get_file_hash(content)
        timestamp = datetime.datetime.now().isoformat()
        base_name = os.path.basename(file_path)
        snapshot_dir = get_snapshot_dir(base_name)

        # 存储原始文件副本
        snapshot_file_path = os.path.join(snapshot_dir, f"{timestamp}.bak")
        os.makedirs(snapshot_dir, exist_ok=True)
        shutil.copy(file_path, snapshot_file_path)

        # 存储元信息
        metadata = {
            "file": base_name,
            "timestamp": timestamp,
            "hash": file_hash,
            "snapshot_path": snapshot_file_path,
            "remark": remark,
        }
        self.version_db.save_version(base_name, metadata)
        return metadata

    def _get_strategy(self, file_path: str):
        for s in self.strategies:
            if s.supports(file_path):
                return s
        return None