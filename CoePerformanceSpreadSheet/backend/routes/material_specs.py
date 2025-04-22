from fastapi import APIRouter
from pydantic import BaseModel
import math
# Import the shared lookup table helper function:
from .utils.lookup_tables import get_material

router = APIRouter()

# Expanded payload to support all four views: Max, Full, Min, and Width.
class MaterialSpecsPayload(BaseModel):
    # Max view
    materialTypeMax: str = None
    materialThicknessMax: float = None  # in inches
    yieldStrengthMax: float = None       # in psi
    coilWidthMax: float = None           # in inches
    coilWeightMax: float = None          # in lbs
    coilIDMax: float = None              # in inches

    # Full view
    materialTypeFull: str = None
    materialThicknessFull: float = None
    yieldStrengthFull: float = None
    coilWidthFull: float = None
    coilWeightFull: float = None
    coilIDFull: float = None

    # Min view
    materialTypeMin: str = None
    materialThicknessMin: float = None
    yieldStrengthMin: float = None
    coilWidthMin: float = None
    coilWeightMin: float = None
    coilIDMin: float = None

    # Width view
    materialTypeWidth: str = None
    materialThicknessWidth: float = None
    yieldStrengthWidth: float = None
    coilWidthWidth: float = None
    coilWeightWidth: float = None
    coilIDWidth: float = None

def calculate_variant(materialType, thickness, yield_strength, coil_width, coil_weight, coil_id):
    # Look up material properties using our shared lookup.
    try:
        mat = get_material(materialType)
    except ValueError:
        mat = {}  # Could choose to default to an empty dict if not provided.
        
    modulus = mat.get("modulus")
    density = mat.get("density")
    
    # === Minimum Bend Radius Calculation (in inches) ===
    if thickness and yield_strength and modulus:
        min_bend_radius = round((modulus * (thickness / 2)) / yield_strength, 4)
    else:
        min_bend_radius = 0

    # === Minimum Loop Length Calculation (in feet) ===
    if min_bend_radius > 0:
        min_loop_length = round((min_bend_radius * 4) / 12, 4)
    else:
        min_loop_length = 0

    # === Coil O.D. Calculated ===
    if coil_width and coil_weight and coil_id and density:
        try:
            area_term = coil_weight / (density * math.pi * coil_width)
            radius_term = (coil_id / 2) ** 2
            coil_od = math.sqrt(area_term + radius_term) * 2
            coil_od_calculated = math.ceil(coil_od)
        except Exception:
            coil_od_calculated = ""
    else:
        coil_od_calculated = ""
    
    return {
        "minBendRadius": min_bend_radius,
        "minLoopLength": min_loop_length,
        "coilODCalculated": coil_od_calculated
    }

@router.post("/calculate")
def calculate_specs(payload: MaterialSpecsPayload):
    results = {}
    # Process each view (Max, Full, Min, and Width) individually.
    for view in ["Max", "Full", "Min", "Width"]:
        mType = getattr(payload, f"materialType{view}", None)
        thickness = getattr(payload, f"materialThickness{view}", None)
        yld = getattr(payload, f"yieldStrength{view}", None)
        cWidth = getattr(payload, f"coilWidth{view}", None)
        cWeight = getattr(payload, f"coilWeight{view}", None)
        cID = getattr(payload, f"coilID{view}", None)

        computed = calculate_variant(mType, thickness, yld, cWidth, cWeight, cID)
        results[f"minBendRadius{view}"] = computed["minBendRadius"]
        results[f"minLoopLength{view}"] = computed["minLoopLength"]
        results[f"coilODCalculated{view}"] = computed["coilODCalculated"]

    return results
