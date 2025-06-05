import os
import shutil
import datetime
import uuid
from typing import List, Dict, Optional
from typing import Tuple
from pathlib import Path
from core.platform_utils import get_app_data_dir

# Central snapshot directory (cross‑platform)
SNAP_ROOT = Path(get_app_data_dir()) / "snapshots"
SNAP_ROOT.mkdir(parents=True, exist_ok=True)

from PyQt5.QtCore import QObject, pyqtSignal

from .version_db import SnapshotRepository
from .diff_engine import DiffEngine
from .snapshot_loaders.loader_registry import LoaderRegistry


class SnapshotManager(QObject):
    """
    Central service class that coordinates snapshot creation, deletion, listing,
    content retrieval and diff operations.  All UI layers should depend on this
    class rather than talking directly to the repository or the file‑system.
    """

    snapshot_created = pyqtSignal(dict)   # metadata dict emitted after creation
    snapshot_deleted = pyqtSignal(dict)   # metadata dict emitted after deletion

    def __init__(self,
                 repository: Optional[SnapshotRepository] = None,
                 diff_engine: Optional[DiffEngine] = None):
        super().__init__()
        # Dependency injection: allows easy replacement in tests or future cloud repo.
        self.repo = repository or SnapshotRepository()
        self.diff_engine = diff_engine or DiffEngine()
        # stack of (doc_name, undo_meta, restore_meta) for undo feature
        self._undo_stack: List[Tuple[str, Dict, Dict]] = []

    # ------------------------------------------------------------------ public API

    def create_snapshot(self, file_path: str, remark: str = "") -> Dict:
        """
        Create a new snapshot from `file_path`.

        :param file_path: Absolute path of the source document.
        :param remark:    Optional commit message / remark string.
        :return:          Metadata dict describing the new snapshot.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(file_path)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        doc_name = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1]  # keep original extension (e.g., ".txt")
        # Store snapshots under ~/Library/Application Support/DocSnap/snapshots/<doc_name>/
        snapshot_dir = SNAP_ROOT / os.path.basename(file_path)
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        snapshot_id = f"{timestamp}_{uuid.uuid4().hex[:6]}"
        snapshot_file = snapshot_dir / f"{snapshot_id}{ext}"

        # 1. copy file bytes (default saver behaviour)
        shutil.copyfile(file_path, str(snapshot_file))

        # 2. prepare metadata & persist
        meta = {
            "snapshot_id": snapshot_id,
            "file": doc_name,
            "file_path": file_path,          # absolute path of original doc
            "timestamp": timestamp,
            "remark": remark,
            "snapshot_path": str(snapshot_file)
        }
        self.repo.save_version(doc_name, meta)
        # register a fallback plain‑text loader for legacy '.bak' if not yet registered
        if LoaderRegistry.get_loader(".bak") is None:
            class _BakFallbackLoader:
                def get_text(self, fp):  # simplistic; tries text read
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                            return f.read()
                    except Exception:
                        return "(binary content)"
                def load_structured(self, fp):
                    return self.get_text(fp)
            LoaderRegistry.register_loader(".bak", _BakFallbackLoader())
        # emit signal for UI refresh
        self.snapshot_created.emit(meta)
        return meta

    def delete_snapshot(self, doc_name: str, version_meta: Dict) -> None:
        """
        Delete snapshot file and remove metadata entry.
        """
        snapshot_path = version_meta.get("snapshot_path")
        if snapshot_path and os.path.exists(snapshot_path):
            os.remove(snapshot_path)
        self.repo.remove_version(doc_name, version_meta)
        # emit signal for UI refresh
        self.snapshot_deleted.emit(version_meta)

    def list_snapshots(self, doc_name: str) -> List[Dict]:
        """
        Return list of snapshot metadata for given document, newest first.
        """
        self.repo.reload()
        versions = self.repo.get_versions(doc_name)
        versions.sort(key=lambda v: v.get("timestamp", ""), reverse=True)
        return versions

    def get_snapshot_content(self, snapshot_path: str) -> str:
        """
        Return textual content of snapshot using the registered loader.

        Parameters
        ----------
        snapshot_path : str
            Absolute path to the snapshot file.

        Returns
        -------
        str
            Plain‑text content extracted by the appropriate SnapshotLoader.

        Raises
        ------
        ValueError
            If no loader is registered for the file extension.
        """
        _, ext = os.path.splitext(snapshot_path)
        loader = LoaderRegistry.get_loader(ext)
        if loader is None:
            raise ValueError(f"Unsupported snapshot format: {ext}")
        return loader.get_text(snapshot_path)

    def compare_snapshots(self, path1: str, path2: str) -> str:
        """
        Use injected DiffEngine to compare two snapshot files.
        """
        return self.diff_engine.compare_files(path1, path2)


    # ----------------- restore / undo -----------------
    def restore_snapshot(self, target_meta: Dict):
        """
        Safely restore working document to the state of target_meta.
        1) create auto-backup of current doc (undo point)
        2) overwrite current doc with snapshot content
        3) create new snapshot entry 'Restore to <id>'
        """
        snap_id = target_meta.get("snapshot_id") or os.path.splitext(os.path.basename(target_meta.get("snapshot_path", "")))[0]
        work_file = self._get_work_file(target_meta)

        # 1. backup current state
        backup_meta = self.create_snapshot(
            work_file,
            remark=f"Auto backup before restore -> {snap_id}"
        )

        # 2. overwrite
        shutil.copyfile(target_meta["snapshot_path"], work_file)

        # 3. add new snapshot indicating restore
        restore_meta = self.create_snapshot(
            work_file,
            remark=f"Restore to {snap_id}"
        )

        # push undo stack
        self._undo_stack.append((target_meta.get("file", ""), backup_meta, restore_meta))

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def undo_restore(self):
        """Undo the most recent restore operation."""
        if not self._undo_stack:
            return
        doc_name, backup_meta, restore_meta = self._undo_stack.pop()
        # restore to backup_meta (this will push another entry, but we don't push recursively)
        work_file = self._get_work_file(backup_meta)
        shutil.copyfile(backup_meta["snapshot_path"], work_file)
        self.create_snapshot(work_file, remark="Undo Restore")


    # ----------------- internal helpers -----------------
    def _get_work_file(self, meta: Dict) -> str:
        """
        Return absolute path to the original working document.
        Prefer meta['file_path']; fallback to old heuristic.
        """
        # 1) preferred absolute path
        fp = meta.get("file_path")
        if fp and os.path.exists(fp):
            return fp

        # 2) fallback heuristic (legacy snapshots)
        snap_path = meta["snapshot_path"]
        doc_name = meta["file"]
        doc_dir = os.path.dirname(os.path.dirname(snap_path))  # parent of .docsnap
        return os.path.join(doc_dir, doc_name)
