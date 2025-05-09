"""
snapshot_loaders package
========================
Import loader plugin modules here so that they register themselves with
LoaderRegistry at application start‑up.

Add new loader imports below (e.g., docx_loader, json_loader) as you
implement additional formats.
"""

# Import loader plugins (auto‑register via LoaderRegistry)
from . import txt_loader  # noqa: F401  (imported for side‑effects)
from . import docx_loader   # noqa: F401
# Future loaders:
# from . import docx_loader
# from . import json_loader
# from . import markdown_loader
