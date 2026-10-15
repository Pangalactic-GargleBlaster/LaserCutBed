"""Check native Bed joint groups against temporary model copies."""
import argparse
from pathlib import Path
import shutil
import sys
import tempfile
import traceback

import FreeCAD as App
import finger_joint
import joint_group

ROOT = Path(__file__).resolve().parents[1]
from shared_paths import design_system_root
sys.path.insert(0, str(design_system_root() / "tools"))
from set_fcstd_visibility import set_visibility


def validate(doc, height, ply):
    errors = [(obj.Name, obj.State) for obj in doc.Objects if "Invalid" in obj.State]
    assert not errors, errors
    bodies = [obj for obj in doc.Objects if obj.TypeId == "PartDesign::Body"]
    assert len(bodies) == 320
    for body in bodies:
        assert body.Tip is not None, body.Name
        shape = body.Tip.Shape
        assert not shape.isNull() and shape.isValid() and len(shape.Solids) == 1, body.Name
    for index in range(1, 9):
        top = doc.getObject(f"Cabinet{index}TopOuter")
        assert abs(top.Z.Value + top.Height.Value - height) < 1e-6
        assert abs(top.Height.Value - ply) < 1e-6
        assert abs(doc.getObject(f"Cabinet{index}TopOuterBody").Tip.Shape.BoundBox.ZMax
                   - height) < 1e-5
    plans = [o for o in doc.Objects if isinstance(getattr(o, "Proxy", None), joint_group.GroupPlanProxy)]
    assert plans, "No native joint plans found"
    assert any(p.SourceCount == 2 for p in plans), "Laminated sources were not grouped"
    assert not any(isinstance(getattr(o, "Proxy", None), finger_joint.SourceJointProxy)
                   for o in doc.Objects), "Legacy joint features remain"
    for plan in plans:
        assert plan.SourceCount >= 1 and plan.ReceivingCount >= 1, plan.Name
    print("VALID", height, ply, "320 bodies", flush=True)


def check():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "Bed.FCStd")
    args = parser.parse_args()
    print("WORKBENCH", joint_group.__file__, flush=True)
    with tempfile.TemporaryDirectory(prefix="bed-live-joints-") as folder:
        path = str(Path(folder) / "Bed.FCStd")
        shutil.copy2(args.model, path)
        doc = App.openDocument(path)
        try:
            params = doc.BedParameters
            height, ply = params.BedHeight.Value, params.ply.Value
            fingers = params.NumberOfFingers
            params.BedHeight = height + 25.4
            params.ply = ply + 0.2
            params.NumberOfFingers = max(1, fingers - 1)
            doc.recompute()
            validate(doc, height + 25.4, ply + 0.2)
            params.BedHeight = height
            params.ply = ply
            params.NumberOfFingers = fingers
            doc.recompute()
            validate(doc, height, ply)
            doc.save()
        finally:
            App.closeDocument(doc.Name)
        set_visibility(path)
        doc = App.openDocument(path)
        try:
            doc.recompute()
            validate(doc, height, ply)
            print("PASS: live bed height, plywood thickness, finger count, restore, save/reopen", flush=True)
        finally:
            App.closeDocument(doc.Name)


try:
    check()
except Exception:
    traceback.print_exc()
    raise SystemExit(1)
