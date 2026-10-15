"""Select exactly the Design System checkout requested by the Bed project."""
import importlib
import json
import os
from pathlib import Path
import sys

from shared_paths import design_system_root

ENTRYPOINT = Path(__file__).with_name('freecad_entrypoint.py')


def load_design_system():
    root = design_system_root()
    directory = root / 'freecad/DesignSystem'
    # FreeCAD's installed Init.py runs first and may preload another checkout.
    names = {p.stem for p in directory.glob('*.py')} - {'Init', 'InitGui'}
    for name in names:
        sys.modules.pop(name, None)
    sys.path.insert(0, str(directory))
    for name in ('panel', 'drawer_components', 'finger_joint', 'joint_group'):
        importlib.import_module(name)
    print('DESIGN_SYSTEM_RUNTIME', root, flush=True)
    return root


def invocation(command, script, arguments, environment):
    env = environment.copy()
    env['BED_FREECAD_SCRIPT'] = str(Path(script).resolve())
    env['BED_FREECAD_ARGUMENTS'] = json.dumps(list(arguments))
    if Path(script).name in ('check_overlaps.py', 'audit_panel_symmetry.py') and arguments:
        env['PANEL_MODEL_PATH'] = str(Path(arguments[0]).resolve())
    return [str(command), str(ENTRYPOINT)], env
