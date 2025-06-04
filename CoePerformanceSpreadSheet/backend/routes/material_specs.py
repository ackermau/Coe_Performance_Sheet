from fastapi import APIRouter
from pydantic import BaseModel
import math
# Import the shared lookup table helper function:
from .utils.lookup_tables import get_material

router = APIRouter()

# Expanded payload to support all four views: Max, Full, Min, and Width.
class MaterialSpecsPayload(BaseModel):
    # Max view
    material_type_max: str = None
    material_thickness_max: float = None  # in inches
    yield_strength_max: float = None       # in psi
    coil_width_max: float = None           # in inches
    coil_weight_max: float = None          # in lbs
    coil_id_max: float = None              # in inches

    # Full view
    material_type_full: str = None
    material_thickness_full: float = None
    yield_strength_full: float = None
    coil_width_full: float = None
    coil_weight_full: float = None
    coil_id_full: float = None

    # Min view
    material_type_min: str = None
    material_thickness_min: float = None
    yield_strength_min: float = None
    coil_width_min: float = None
    coil_weight_min: float = None
    coil_id_min: float = None

    # Width view
    material_type_width: str = None
    material_thickness_width: float = None
    yield_strength_width: float = None
    coil_width_width: float = None
    coil_weight_width: float = None
    coil_id_width: float = None

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
        "min_bend_radius": min_bend_radius,
        "min_loop_length": min_loop_length,
        "coil_od_calculated": coil_od_calculated
    }

@router.post("/calculate")
def calculate_specs(payload: MaterialSpecsPayload):
    results = {}
    # Process each view (Max, Full, Min, and Width) individually.
    for view in ["max", "full", "min", "width"]:
        mType = getattr(payload, f"material_type_{view}", None)
        thickness = getattr(payload, f"material_thickness_{view}", None)
        yld = getattr(payload, f"yield_strength_{view}", None)
        cWidth = getattr(payload, f"coil_width_{view}", None)
        cWeight = getattr(payload, f"coil_weight_{view}", None)
        cID = getattr(payload, f"coil_id_{view}", None)

        computed = calculate_variant(mType, thickness, yld, cWidth, cWeight, cID)
        results[f"min_bend_radius_{view}"] = computed["min_bend_radius"]
        results[f"min_loop_length_{view}"] = computed["min_loop_length"]
        results[f"coil_od_calculated_{view}"] = computed["coil_od_calculated"]

    return results
