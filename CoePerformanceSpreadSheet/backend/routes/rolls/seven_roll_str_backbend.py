from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field
from math import pi, sqrt
import re

from ..utils.lookup_tables import (
    get_material_density,
    get_str_model_value,
);

router = APIRouter()

class RollStrBackbendInput(BaseModel):
    yield_strength: float
    thickness: float
    width: float
    coil_id: float
    coil_od: float
    coil_weight: float

@router.post("/calculate")
def calculate_seven_roll_str_backbend(data: RollStrBackbendInput):
    # Lookups
    try:
        density = get_material_density()
        str_roll_dia = get_str_model_value(data.str_model, "roll_diameter", "str_roll_dia")
        center_dist = get_str_model_value(data.str_model, "center_distance", "center_dist")
        jack_force_available = get_str_model_value(data.str_model, "jack_force_avail", "jack_force_available")
        max_roll_depth_without_material = get_str_model_value(data.str_model, "min_roll_depth", "max_roll_depth_without_material")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in lookup: {e}")
    
    # MAx Roller Depth with material
    check = ((str_roll_dia + data.thickness) ** 2) - ((center_dist / 2) ** 2)
    max_roll_depth_with_material = max_roll_depth_without_material
    
    if (str_roll_dia - sqrt(check)) < -str_roll_dia and check >= 0:
        max_roll_depth_with_material = -str_roll_dia + sqrt(check)
    
    return {
        "roll_diameter": round(str_roll_dia, 3),
        "center_distance": center_dist,
        "jack_force_available": jack_force_available,
        "max_roll_depth_without_material": round(max_roll_depth_without_material, 3),
        "max_roll_depth_with_material": round(max_roll_depth_with_material, 3),
    }