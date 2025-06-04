from fastapi import APIRouter
from pydantic import BaseModel
from ..services.feed_calculations import (
    run_allen_bradley_calculation
)

router = APIRouter()

class SigmaFiveAllenBradleyInput(BaseModel):
    feed_model: str
    width: int
    loop_pit: str
    
    material_type: str
    application: str
    type_of_line: str
    roll_width: str
    feed_rate: float
    material_width: int 
    material_thickness: float
    press_bed_length: int

    friction_in_die: float
    acceleration_rate: float
    chart_min_length: float
    length_increment: float
    feed_angle_1: float
    feed_angle_2: float
    

@router.post("/calculate")
def calculate_allen_bradley(data: SigmaFiveAllenBradleyInput):
    result = run_allen_bradley_calculation(data, "allen_bradley")
    return result
