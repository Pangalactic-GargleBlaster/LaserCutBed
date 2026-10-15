"""Run a script using Bed's selected Design System and FreeCAD runtime."""
import importlib.util
import os
import subprocess
import sys

from freecad_runtime import invocation
from shared_paths import design_system_root


if __name__ == '__main__':
    root = design_system_root()
    args = sys.argv[1:]
    if args and args[0] == '--shared':
        if len(args) < 2:
            raise SystemExit('--shared requires a script name')
        args = [str(root / 'tools' / args[1]), *args[2:]]
    if not args:
        raise SystemExit('Provide a Python script')
    spec = importlib.util.spec_from_file_location('design_system_launcher', root / 'tools/run_freecad.py')
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    command = launcher.freecad_command()
    if command is None:
        raise SystemExit('FreeCADCmd not found; set FREECAD_CMD to its full path')
    if args[0] in ('--version', '--help', '-v', '-h'):
        raise SystemExit(subprocess.call([command, *args]))
    cmd, env = invocation(command, args[0], args[1:], os.environ)
    raise SystemExit(subprocess.call(cmd, env=env))
