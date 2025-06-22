import os
import json
from pathlib import Path
from core.platform_utils import get_app_data_dir

class SnapshotRepository:
    """
    SnapshotRepository is responsible for managing snapshot metadata,
    including saving, retrieving, and deleting version entries from disk.
    """
    def __init__(self, db_path: str | None = None):
        """
        If *db_path* is None, place the versions database in the
        per‑user application data directory, e.g.:

          • macOS : ~/Library/Application Support/DocSnap/versions.json
          • Windows: %APPDATA%\DocSnap\versions.json
        """
        if db_path is None:
            db_path = Path(get_app_data_dir()) / "versions.json"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.db_path.exists():
            self.db_path.write_text("{}")

        # load existing data
        with self.db_path.open("r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save_version(self, doc_name, metadata: dict):
        self.data.setdefault(doc_name, []).append(metadata)
        self.save()

    def get_versions(self, doc_name) -> list:
        return self.data.get(doc_name, [])
    
    def remove_version(self, doc_name, target_version):
        if doc_name not in self.data:
            return
        self.data[doc_name] = [v for v in self.data[doc_name] if v != target_version]
        self.save()

    def save(self):
        with self.db_path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def reload(self):
        """从磁盘重新加载版本数据"""
        with open(self.db_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
