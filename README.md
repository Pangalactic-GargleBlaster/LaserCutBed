# Bed project

`Bed.FCStd` is the current parametric model. `tools/generate_bed.py` builds it
from `design_parameters.json`; `packing_config.json` describes the bodies and
assembly groups used for laser sheet layout.

The reusable FreeCAD workbench and manufacturing tools are in the
[Design System](https://github.com/Pangalactic-GargleBlaster/FreeCAD-Laser-Cutting-Design-System)
repository. After cloning, run `git submodule update --init` to fetch the
version pinned by this project. Alternatively, set `DESIGN_SYSTEM_ROOT` to a
separate checkout of that repository.

From this repository's root:

```text
python3 tools/run_freecad.py tools/generate_bed.py
python3 tools/run_freecad.py --shared check_overlaps.py Bed.FCStd
python3 tools/run_freecad.py --shared audit_panel_symmetry.py Bed.FCStd
python3 tools/build_manufacturing.py --check-only
python3 tools/build_manufacturing.py
```

The manufacturing script reads the current saved `Bed.FCStd`; it does not
regenerate or change the model. It exports face-up DXFs, places parts on
1193.8 × 787.4 mm sheets, adds filigree engravings, and publishes validated
files in `manufacturing/`. Rebuild those files after changing the model.
