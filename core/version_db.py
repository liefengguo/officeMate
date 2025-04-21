import os
import json

class VersionDB:
    def __init__(self):
        self.db_path = os.path.expanduser("~/Documents/docsnap/versions.json")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump({}, f)

    def save_version(self, doc_name, metadata: dict):
        with open(self.db_path, "r") as f:
            db = json.load(f)
        db.setdefault(doc_name, []).append(metadata)
        with open(self.db_path, "w") as f:
            json.dump(db, f, indent=2)

    def get_versions(self, doc_name) -> list:
        with open(self.db_path, "r") as f:
            db = json.load(f)
        return db.get(doc_name, [])
