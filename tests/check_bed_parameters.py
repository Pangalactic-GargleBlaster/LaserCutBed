"""Run with tools/run_freecad.py; checks use temporary documents only."""
import importlib.util
import os
from pathlib import Path
import sys

import FreeCAD as App

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("bed_generator_under_test", ROOT / "tools/generate_bed.py")
bed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bed)


def valid_bodies(doc):
    bodies = [obj for obj in doc.Objects if obj.TypeId == "PartDesign::Body"]
    assert len(bodies) == 320, len(bodies)
    for body in bodies:
        assert body.Tip is not None, body.Name
        assert not body.Tip.Shape.isNull(), body.Name
        assert body.Tip.Shape.isValid(), body.Name
    errors = [(obj.Name, obj.State) for obj in doc.Objects if "Invalid" in obj.State]
    assert not errors, errors
    return bodies


def check():
    doc = App.newDocument("ParameterCheck")
    try:
        params = bed.add_parameters(doc)
        assert abs(params.BedHeight.Value - bed.DEFAULT_BED_HEIGHT) < 1e-7
        params.BedHeight = "17 in"
        params.DrawerClearance = 4.5
        params.setExpression("LargeDrawerBoxWidth", "29 in - 12 * ply")
        before = list(params.ExpressionEngine)
        assert bed.add_parameters(doc) is params
        assert abs(params.BedHeight.Value - 431.8) < 1e-7
        assert params.DrawerClearance.Value == 4.5
        assert list(params.ExpressionEngine) == before
        copied = App.newDocument("CopiedParameters")
        try:
            copied.copyObject(params)
            bed.add_parameters(copied)
            assert abs(copied.BedParameters.BedHeight.Value - 431.8) < 1e-7
            assert copied.BedParameters.DrawerClearance.Value == 4.5
            assert list(copied.BedParameters.ExpressionEngine) == before
        finally:
            App.closeDocument(copied.Name)
        params.removeProperty("BedHeight")
        bed.add_parameters(doc)
        assert abs(params.BedHeight.Value - bed.DEFAULT_BED_HEIGHT) < 1e-7
        assert params.DrawerClearance.Value == 4.5
    finally:
        App.closeDocument(doc.Name)
    if os.environ.get("BED_PARAMETERS_ONLY") == "1":
        print("PASS: missing defaults, saved values/expressions, copied variable set", flush=True)
        return
    model = App.openDocument(str(ROOT / "Bed.FCStd"))
    try:
        model.recompute()
        bodies = valid_bodies(model)
        original_height = model.BedParameters.BedHeight.Value
        for index in range(1, 9):
            top = model.getObject(f"Cabinet{index}TopOuter")
            assert abs(top.Z.Value + top.Height.Value - original_height) < 1e-6
            assert dict(top.ExpressionEngine)["Z"] == "BedParameters.BedHeight - BedParameters.ply"
        print("PASS: defaults, saved overrides/expressions, copied variable set, 320 valid bodies, parameter-driven top surfaces", flush=True)
    finally:
        App.closeDocument(model.Name)


try:
    check()
except Exception:
    import traceback
    traceback.print_exc()
    raise SystemExit(1)
