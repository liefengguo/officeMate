import os
import json

class RecentDocDB:
    def __init__(self):
        self.path = os.path.expanduser("~/.docsnap/recent_docs.json")
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