import os


def get_snapshot_dir(doc_name: str) -> str:
    base_dir = os.path.expanduser("~/Documents/docsnap/snapshots")
    return os.path.join(base_dir, doc_name)
