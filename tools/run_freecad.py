"""Run a project script with the shared Design System FreeCAD launcher."""

import subprocess
import sys

from shared_paths import design_system_root


if __name__ == "__main__":
    runner = design_system_root() / "tools" / "run_freecad.py"
    args = sys.argv[1:]
    if args and args[0] == "--shared":
        if len(args) < 2:
            raise SystemExit("--shared requires a script name")
        args = [str(design_system_root() / "tools" / args[1]), *args[2:]]
    raise SystemExit(subprocess.call([sys.executable, str(runner), *args]))
