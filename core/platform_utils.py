

"""
platform_utils.py
~~~~~~~~~~~~~~~~~

Platform‑specific helpers for OfficeMate.

* **is_dark_mode()** – Detect whether the OS is currently using a dark appearance.
* **get_app_data_dir()** – Return a writable, per‑user directory that follows
  platform conventions (macOS Application Support, Windows %APPDATA%, etc.).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths

try:  # Windows registry is only available on Windows
    import winreg
except ModuleNotFoundError:  # pragma: no cover
    winreg = None  # type: ignore


# ---------------------------------------------------------------------- dark‑mode
def is_dark_mode() -> bool:  # noqa: D401 – simple function
    """Return **True** if the operating system is set to *dark* appearance.

    Currently supports macOS (10.14+) and Windows 10/11.  
    Other platforms default to *False* (light).
    """
    if sys.platform == "darwin":
        # macOS checks the global AppleInterfaceStyle. When set to "Dark", the
        # system is in dark appearance. An empty result → light mode.
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=0.5,
            )
            return result.stdout.strip() == "Dark"
        except Exception:
            return False

    if sys.platform.startswith("win"):
        # Windows 10/11 registry key:
        #   HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize
        #   - AppsUseLightTheme (DWORD): 0 = dark, 1 = light
        if winreg is None:  # pyright: ignore[reportGeneralTypeIssues]
            return False
        try:
            with winreg.OpenKey(  # type: ignore[attr-defined]
                winreg.HKEY_CURRENT_USER,  # type: ignore[attr-defined]
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            ) as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")  # type: ignore[attr-defined]
            return value == 0
        except (FileNotFoundError, OSError):
            return False

    # Linux / other – could inspect GTK/KDE settings, but keep simple for now.
    return False


# ------------------------------------------------------------------- data paths
def get_app_data_dir(subfolder: str = "OfficeMate") -> Path:
    """Return a per‑user *application data* directory suitable for storing files.

    * macOS : ``~/Library/Application Support/<subfolder>``
    * Windows: ``%APPDATA%\\<subfolder>``
    * Linux  : ``~/.local/share/<subfolder>``  (fallback)

    The directory is **created if it does not already exist**.
    """
    # QStandardPaths chooses the right location for us.
    base_dir_str = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    base = Path(base_dir_str) if base_dir_str else Path()

    # Fallback if Qt failed to provide a path (rare but possible)
    if not base:
        if sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        elif sys.platform.startswith("win"):
            appdata = os.getenv("APPDATA") or (Path.home() / "AppData" / "Roaming")
            base = Path(appdata)
        else:  # generic *nix fallback
            base = Path.home() / ".local" / "share"

    # Ensure subfolder included once
    if subfolder and subfolder not in base.parts:
        base = base / subfolder

    base.mkdir(parents=True, exist_ok=True)
    return base