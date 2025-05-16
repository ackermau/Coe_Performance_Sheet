from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from math import pi, sqrt
import re

# Import your lookup functions
from ..utils.lookup_tables import get_material_density, get_sigma_five_specs;
from .physics.inertia import calculate_total_refl_inertia

router = APIRouter()

class SigmaFiveInput(BaseModel):
    feed_model: str
    width: int
    loop_pit: str
    full_width_rolls: str
    material_type: str

    material_width: int 
    material_thickness: float
    press_bed_length: int
    
    friction_in_die: float
    acceleration_rate: float
    chart_min_length: float
    length_increment: float
    feed_angle_1: float
    feed_angle_2: float

    g_box_qty: int
    g_box_inertia: float
    g_box_ratio: float
    g_box_refl_inertia: float

@router.post("/calculate")
def calulate_sigma_five(data: SigmaFiveInput):
    # Lookups
    try:
        density = get_material_density(data.material_type)
        max_motor_rpm = get_sigma_five_specs(data.feed_model, "max_mtr_rpm", "max_motor_rpm")
        motor_inertia = get_sigma_five_specs(data.feed_model, "mot_inertia", "motor_inertia")
        motor_peak_torque = get_sigma_five_specs(data.feed_model, "mot_peak_torque", "motor_peak_torque")
        motor_rms_torque = get_sigma_five_specs(data.feed_model, "mot_rms_tq", "motor_rms_torque")
        l_roll = get_sigma_five_specs(data.feed_model, "l_roll", "lower_roll")
        u_roll = get_sigma_five_specs(data.feed_model, "u_roll", "upper_roll")
        ratio = get_sigma_five_specs(data.feed_model, "ratio", "ratio")
        efficiency = get_sigma_five_specs(data.feed_model, "efficiency", "efficiency")
        settle_torque = get_sigma_five_specs(data.feed_model, "settle_tor", "settle_torque")
        friction_torque = get_sigma_five_specs(data.feed_model, "fric_torque", "friction_torque")

        InertiaInput = {
            "feed_model": data.feed_model,
            "width": data.width,
            "thickness": data.material_thickness,
            "press_bed_length": data.press_bed_length,
            "material_loop": data.material_width,
            "ratio": ratio,
            "efficiency": efficiency,
            "u_roll": u_roll,
            "l_roll": l_roll,
            "g_box_qty": data.g_box_qty,
            "g_box_inertia": data.g_box_inertia, 
            "g_box_ratio": data.g_box_ratio, 
            "g_box_refl_inertia": data.g_box_refl_inertia,
        }

        refl_inertia = calculate_total_refl_inertia(InertiaInput, qty=data.g_box_qty, length=data.press_bed_length)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid material type")