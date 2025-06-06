from fastapi import APIRouter
from ..services.hyd_shear_calculations import calculate_hyd_shear, HydShearInput

router = APIRouter()

@router.post("/calculate")
def calculate_single_rake_hyd_shear(data: HydShearInput, spec_type: str = "single_rake"):
    return calculate_hyd_shear(data, spec_type)