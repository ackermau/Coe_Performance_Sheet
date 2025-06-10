from fastapi import APIRouter
from ..services.hyd_shear_calculations import calculate_hyd_shear
from models import HydShearInput

router = APIRouter()

@router.post("/calculate")
def calculate_bow_tie_hyd_shear(data: HydShearInput, spec_type: str = "bow_tie"):
    return calculate_hyd_shear(data, spec_type)