"""FreeCADCmd bootstrap; run the selected project/shared script after loading it."""
import json
import os
from pathlib import Path
import runpy
import sys
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
from freecad_runtime import load_design_system

try:
    load_design_system()
    script = os.environ['BED_FREECAD_SCRIPT']
    arguments = json.loads(os.environ.get('BED_FREECAD_ARGUMENTS', '[]'))
    sys.argv = [script, *arguments]
    sys.path.insert(0, str(Path(script).parent))
    runpy.run_path(script, run_name='__main__')
except Exception:
    traceback.print_exc()
    raise SystemExit(1)
