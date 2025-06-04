from fastapi import APIRouter
from pydantic import BaseModel
from ..services.feed_calculations import run_sigma_five_calculation, run_sigma_five_pt_calculation

router = APIRouter()

class SigmaFivePTInput(BaseModel):
    feed_model: str
    width: int
    loop_pit: str

    material_type: str
    application: str
    type_of_line: str
    roll_width: str
    material_width: int 
    material_thickness: float
    press_bed_length: int

    friction_in_die: float
    acceleration_rate: float
    chart_min_length: float
    length_increment: float
    feed_angle_1: float
    feed_angle_2: float

    straightening_rolls: int
    yield_strength: float
    str_pinch_rolls: str
    req_max_fpm: float

@router.post("/calculate")
def calculate_sigma_five_pt(data: SigmaFivePTInput):

    base_result = run_sigma_five_calculation(data, "sigma_five_pt")
    pt_result = run_sigma_five_pt_calculation(base_result, 
                data.straightening_rolls, data.material_width, data.material_thickness, 
                data.feed_model, data.yield_strength, data.str_pinch_rolls, data.req_max_fpm, "sigma_five_pt")
    
    base_result["peak_torque"] += pt_result["straightner_torque"]

    result = base_result | pt_result

    return result