"""Exercise intersecting laminated cabinet joints using the native API."""
import importlib.util
from pathlib import Path
import sys
import FreeCAD as App

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("bed_generator", ROOT / "tools/generate_bed.py")
bed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bed)
doc = App.newDocument("NativeBedCabinet")
try:
    params = bed.add_parameters(doc)
    params.ply = 5.8
    doc.recompute()
    part, layers = bed.create_cabinet(doc, "Cabinet2", "Native cabinet", 1473.2, 0,
                                      "+X", (0.8, 0.6, 0.3))
    doc.recompute()
    bed.add_cabinet_joints(layers, "Cabinet2", 1473.2, 0, "main")
    for height, ply, fingers in ((381, 5.8, 4), (406.4, 5.8, 4), (406.4, 6, 4),
                                 (381, 5.8, 3), (381, 5.8, 4)):
        params.BedHeight = height
        params.ply = ply
        params.NumberOfFingers = fingers
        doc.recompute()
        bodies = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"]
        for body in bodies:
            assert "Invalid" not in body.Tip.State, (body.Name, body.Tip.State)
            assert body.Tip.Shape.isValid() and len(body.Tip.Shape.Solids) == 1, body.Name
        assert abs(doc.Cabinet2TopOuterBody.Tip.Shape.BoundBox.ZMax - height) < 1e-5
        assert not [(o.Name, o.State) for o in doc.Objects if "Invalid" in o.State]
        print("PASS native cabinet", height, ply, fingers, len(bodies), flush=True)
finally:
    App.closeDocument(doc.Name)
