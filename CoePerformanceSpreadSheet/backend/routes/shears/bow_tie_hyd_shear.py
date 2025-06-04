from fastapi import APIRouter
from pydantic import BaseModel
from ..services.hyd_shear_calculations import calculate_hyd_shear

router = APIRouter()

# Hydraulic shear import payload
class HydShearInput(BaseModel):
    max_material_thickness: float
    coil_width: float
    material_tensile: float

    rake_of_blade: float
    overlap: float
    blade_opening: float
    percent_of_penetration: float

    bore_size: float
    rod_dia: float
    stroke: float

    pressure: float

    time_for_down_stroke: float
    dwell_time: float

@router.post("/calculate")
def calculate_bow_tie_hyd_shear(data: HydShearInput, spec_type: str = "bow_tie"):
    return calculate_hyd_shear(data, spec_type)