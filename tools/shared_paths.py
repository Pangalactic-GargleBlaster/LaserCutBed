"""Locate the reusable FreeCAD and manufacturing tools for this project."""

import os
from pathlib import Path


BED_ROOT = Path(__file__).resolve().parent.parent


def design_system_root():
    override = os.environ.get("DESIGN_SYSTEM_ROOT")
    candidates = (
        [Path(override)] if override else
        [BED_ROOT / "design-system", BED_ROOT.parent / "Design System"]
    )
    for candidate in candidates:
        root = candidate.expanduser().resolve()
        if (root / "freecad" / "DesignSystem" / "panel.py").is_file() and (
            root / "tools" / "manufacturing" / "pack_nested_frames.py"
        ).is_file():
            return root
    raise FileNotFoundError(
        "Design System tools not found. Initialize the design-system submodule "
        "or set DESIGN_SYSTEM_ROOT to its checkout."
    )
