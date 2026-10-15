# Bed project

`Bed.FCStd` is the current parametric model. `tools/generate_bed.py` builds it
using defaults from `design_parameters.json`; `packing_config.json` describes
the bodies and assembly groups used for laser sheet layout.

The reusable FreeCAD workbench and manufacturing tools are in the
[Design System](https://github.com/Pangalactic-GargleBlaster/FreeCAD-Laser-Cutting-Design-System)
repository. After cloning, run `git submodule update --init` to fetch the
version pinned by this project. Alternatively, set `DESIGN_SYSTEM_ROOT` to a
separate checkout of that repository. Every project FreeCAD command explicitly
loads proxies from that selected checkout before restoring the model, even if
FreeCAD has already loaded another installed workbench.

Bed uses the Design System's native `create_joint_group` API. Each laminated
source passes the end faces of all its plies in one call, together with the
receiving bodies and the Bed parameter expressions. Result features belong to
their panels; the shared joint controller owns the editable joint parameters.
No Bed-specific startup module is required. The pinned Design System revision includes
native solver corrections for flush and laminated panel joints, receiving-finger
alignment, FreeCAD refinement failures, transformed component placements, and
persistent source-face references for parameter edits that renumber faces.
Each joint group shares its computed result across all affected panels.

For GUI editing, FreeCAD's `Mod/DesignSystem` installation must point to
`design-system/freecad/DesignSystem`. Restart FreeCAD after changing versions.

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
files in `manufacturing/`. The latest sheet exporter provides one
`sheets/map.svg` containing all sheets with their sheet indices and part IDs. Rebuild those files after changing the model.

The validated manufacturing output for the current 15-inch native-joint model
is in `manufacturing-native-api/` (53 panels). The existing `manufacturing/`
folder retains the earlier 16-inch output (60 panels). To rebuild the current
output in its own folder, run
`python3 tools/build_manufacturing.py --output-dir manufacturing-native-api`.

## Bed parameters

Edit **Bed Parameters → BedHeight** in FreeCAD to set the platform height
(default: 15 in / 381 mm). Cabinet panels, drawer frames, slides, and
connector holes reference this parameter. Drawer box heights remain
independently adjustable. Native joint groups recompute their geometry from
the panel inputs and parameter expressions. Restart FreeCAD after updating the Design
System workbench, then reopen the model to load the updated Python proxies.

Regeneration preserves the saved `BedParameters` variable set, including
custom values and expressions; defaults are assigned only to missing
properties. `design_parameters.json` and `BED_PLY_MM` supply the ply default
for new models or a missing ply property, rather than overriding saved edits.
Regeneration rebuilds geometry, so manual edits outside the variable set
are not retained. Rebuild manufacturing files after saving model changes.

Check parameter preservation and saved model geometry with:

```text
python3 tools/run_freecad.py tests/check_bed_parameters.py
```

Check live joint updates with the selected Design System against temporary model
copies (height, plywood thickness, finger count, and saving/reopening):

```text
python3 tools/run_freecad.py tests/check_bed_live_joints.py
python3 tools/run_freecad.py tests/check_native_cabinet.py
python3 tools/run_freecad.py tests/check_native_drawer.py --kind main
python3 tools/run_freecad.py tests/check_native_drawer.py --kind bedside
python3 tools/run_freecad.py design-system/tests/run_freecad_tests.py
```

To generate a comparison without replacing `manufacturing/`, use a separate
output folder, for example:

```text
python3 tools/build_manufacturing.py --output-dir manufacturing-15in
```

To export a different saved model without changing `Bed.FCStd`, add
`--model /absolute/path/to/model.FCStd` to the manufacturing command.
