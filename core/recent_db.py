import os
import json
from pathlib import Path
from .platform_utils import get_app_data_dir

class RecentDocDB:
    def __init__(self):
        base = get_app_data_dir()
        self.path = str(Path(base) / "recent_docs.json")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f)

    def get_all(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def add(self, file_path):
        docs = self.get_all()
        if file_path not in docs:
            docs.insert(0, file_path)
            with open(self.path, "w") as f:
                json.dump(docs, f, indent=2)

    def touch(self, file_path):
        """Move file_path to the top as the most recently used."""
        docs = self.get_all()
        if file_path in docs:
            docs.remove(file_path)
        docs.insert(0, file_path)
        with open(self.path, "w") as f:
            json.dump(docs, f, indent=2)

    def remove(self, file_path):
        """Remove a document from the recent list."""
        docs = self.get_all()
        if file_path in docs:
            docs.remove(file_path)
            with open(self.path, "w") as f:
                json.dump(docs, f, indent=2)
