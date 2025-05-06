import os
import json

class SnapshotRepository:
    """
    SnapshotRepository is responsible for managing snapshot metadata,
    including saving, retrieving, and deleting version entries from disk.
    """
    def __init__(self):
        self.db_path = os.path.expanduser("~/Documents/docsnap/versions.json")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump({}, f)
        with open(self.db_path, "r") as f:
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
        with open(self.db_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def reload(self):
        """从磁盘重新加载版本数据"""
        with open(self.db_path, "r") as f:
            self.data = json.load(f)
