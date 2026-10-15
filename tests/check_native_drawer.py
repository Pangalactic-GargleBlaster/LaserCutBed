"""Exercise a complete drawer assembly before rebuilding the full Bed."""
import argparse
import importlib.util
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import FreeCAD as App

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("bed_generator", ROOT / "tools/generate_bed.py")
bed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bed)
parser = argparse.ArgumentParser()
parser.add_argument("--kind", choices=("main", "bedside"), default="main")
parser.add_argument("--capture-dir", type=Path)
args = parser.parse_args()
doc = App.newDocument("NativeDrawerAssembly")
try:
    params = bed.add_parameters(doc)
    params.ply = 5.8
    doc.recompute()
    color = (0.8, 0.6, 0.3)
    if args.kind == "main":
        part, layers = bed.create_cabinet(doc, "Cabinet1", "Native main cabinet", 508, 0,
                                         "-X", color)
        doc.recompute()
        bed.add_cabinet_joints(layers, "Cabinet1", 508, 0, "main")
        view = [float(v) for v in ET.parse(bed.FILIGREE_SVG).getroot().attrib["viewBox"].split()]
        bed.create_large_drawer(doc, part, layers, "Cabinet1Drawer", "Native drawer",
                                508, 0, "-X", color, (bed.FILIGREE_IMAGE, view[2], view[3]))
    else:
        part, layers = bed.create_bedside_cabinet(doc, "Cabinet7", "Native bedside", 0, 1524, color)
        doc.recompute()
        bed.add_cabinet_joints(layers, "Cabinet7", 0, 1524, "bedside")
        for index in range(2):
            bed.create_bedside_drawer(
                doc, part, layers, f"Cabinet7Drawer{index}", f"Native drawer {index}",
                0, 1524, index, color,
                (bed.FILIGREE_SMALL_LEFT, bed.FILIGREE_SMALL_RIGHT, 454, 323),
            )
    for stage, (height, ply, fingers) in enumerate(((381, 5.8, 4), (406.4, 6, 3), (381, 5.8, 4))):
        params.BedHeight = height
        params.ply = ply
        params.NumberOfFingers = fingers
        doc.recompute()
        invalid = [(o.Name, o.State) for o in doc.Objects if "Invalid" in o.State]
        if args.capture_dir and (stage == 0 or invalid):
            args.capture_dir.mkdir(parents=True, exist_ok=True)
            path = args.capture_dir / f"{args.kind}-{'failure' if invalid else 'baseline'}.FCStd"
            doc.saveAs(str(path))
            bed.set_visibility(path)
            print("CAPTURED", path, flush=True)
        assert not invalid, invalid
        bodies = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"]
        for body in bodies:
            assert body.Tip.Shape.isValid() and len(body.Tip.Shape.Solids) == 1, body.Name
        print("PASS native drawer", args.kind, height, ply, fingers, len(bodies), flush=True)
finally:
    App.closeDocument(doc.Name)
