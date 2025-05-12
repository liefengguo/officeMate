"""
DiffEngine
==========

Central coordinator that selects an appropriate DiffStrategy to compare
two snapshot files.  The concrete strategies live in
`core.diff_strategies` and are registered here in order of priority.

Currently available strategies
------------------------------
1. ParagraphDiffStrategy  – structure‑aware paragraph diff for loaders
   that implement `load_structured` (e.g., DocxLoader).
2. TextDiffStrategy       – fallback line‑level unified diff.

Design principles
-----------------
* Open/Closed – add new strategies without modifying core logic; just
  create a new strategy class and insert it into `self.strategies`.
* Single Responsibility – DiffEngine only handles strategy selection /
  orchestration, not the diff algorithm itself.
* Dependency Inversion – DiffEngine depends on abstract `DiffStrategy`,
  not concrete algorithms.
"""

import os
from pathlib import Path
from typing import List

# strategy imports
from .diff_strategies.paragraph_strategy import ParagraphDiffStrategy
from .diff_strategies.text_strategy import TextDiffStrategy
from .diff_strategies.base_strategy import DiffResult, DiffStrategy
from .snapshot_loaders.loader_registry import LoaderRegistry


class DiffEngine:
    """Selects and executes an appropriate diff strategy."""

    def __init__(self) -> None:
        # Priority‑ordered list of strategies (first to support wins)
        self.strategies: List[DiffStrategy] = [
            ParagraphDiffStrategy(),  # structure‑aware diff
            TextDiffStrategy(),       # fallback
        ]

    # --------------------------------------------------------------------- API
    def compare_files(self, file_a: str, file_b: str) -> str:
        """
        Compare two snapshot files, returning unified diff text for display.
        Structured diff information is preserved inside DiffResult for future
        UI use, but currently only .raw is returned.
        """
        ext_a = Path(file_a).suffix
        ext_b = Path(file_b).suffix
        loader_a = LoaderRegistry.get_loader(ext_a)
        loader_b = LoaderRegistry.get_loader(ext_b)

        for strategy in self.strategies:
            if strategy.supports(loader_a, loader_b):
                try:
                    result: DiffResult = strategy.diff(file_a, file_b)
                    return result.raw if result else "无差异"
                except Exception as exc:
                    return f"对比失败（{strategy.__class__.__name__}）：{exc}"

        return "未找到可用的差异算法"