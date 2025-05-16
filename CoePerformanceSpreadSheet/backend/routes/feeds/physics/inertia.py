from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from math import pi, sqrt

import json
import os

# Build a path to the JSON file relative to this file's location.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_JSON_FILE = os.path.join(_BASE_DIR, "lookup_tables.json")

# Load the JSON file only once at module load time.
with open(_JSON_FILE, "r") as f:
    LOOKUP_DATA = json.load(f)

feed_model_lookup = LOOKUP_DATA.get("lookup_sigma5_feed_pt", {})

# Import your lookup functions
from ...utils.lookup_tables import get_material_density

router = APIRouter()

class InertiaInput(BaseModel):
    feed_model: str
    str_model: str

    width: int
    thickness: float
    press_bed_length: int
    material_loop: float
    ratio: float
    efficiency: float

    u_roll: float
    l_roll: float

    g_box_qty: int
    g_box_inertia: float
    g_box_ratio: float
    g_box_refl_inertia: float

def calculate_length(width: float):
    """
    Calculate length based on width.
    """
    if width < 0:
        raise ValueError("Width must be greater than zero")
    return width + 0.75

def calculate_lbs(o_dia: float, i_dia: float, length: float, density: float, qty: int, ratio: float):
    """
    Calculate weight in lbs for given parameters.
    """
    return ((pi * length * density / 4) * (o_dia ** 2 - i_dia ** 2)) * qty

def calculate_inertia(lbs: float, o_dia: float, i_dia: float):
    """
    Calculate inertia for given parameters.
    """
    return ((lbs / 386.4) * (o_dia ** 2 + i_dia ** 2)) / 8

def compute_refl_inertia(data: InertiaInput, qty: int = 1, length: float = 0):
    """
    Calculate reflected inertia for a given feed model.
    """
    try:
        lbs = calculate_lbs(data.u_roll, data.l_roll, length, data.thickness, qty, data.ratio)
        inertia = calculate_inertia(lbs, data.u_roll, data.l_roll)

        return inertia / (data.ratio ** 2)
    except ValueError:
        raise ValueError("Invalid feed model")

@router.post("/calculate")
def calculate_total_refl_inertia(data: InertiaInput):
    try:
        feed_data = feed_model_lookup[data.feed_model]
        results = 0.0

        # Feed model refl inertia
        for element in feed_data:
            len = calculate_length(data.width)
            results += compute_refl_inertia(data, element["qty"], len)

        # Gearbox refl inertia
        if data.g_box_qty > 0:
            results += (data.g_box_qty * data.g_box_inertia)

        # Material refl inertia
        density = get_material_density(data.str_model)
        material_inertia = ((data.width * data.thickness * data.press_bed_length * density) / 32.3) * (((data.u_roll * 0.5) ** 2) / 144) * 12
        results += (material_inertia / (data.ratio ** 2))

        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        