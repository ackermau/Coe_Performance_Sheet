import math
from re import A
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydantic import Field
from math import e, pi, sqrt
from typing import Optional

from .utils.lookup_tables import (
    get_center_dist, get_str_roll_dia, get_pinch_roll_dia, get_jack_force_available, get_max_roll_depth, get_material_density
)

router = APIRouter()

class StrUtilityInput(BaseModel):
    coil_weight_cap: float
    coil_id: float
    coil_width: float
    thickness: float
    yield_strength: float
    material_type: str
    selected_roll: str
    str_model: str
    str_width: float
    horsepower: float
    feed_rate: float
    auto_brake_compensation: str
    acceleration: float

class Lookups(BaseModel):
    strRollDia : float
    pinchRollDia : float
    centerDist : float
    jackForceAvailable : float
    maxRollDepth : float
    modulus : float
    pinchRollGearTeeth : int
    pinchRollGearDP : int
    strRollGearTeeth : int
    strRollGearDP : int
    faceWidthTeeth : int
    contAngleTeeth : int

class StrUtilityOutput(BaseModel):
    requiredForce: float = Field(..., alias="required_force")
    pinchRoll: float = Field(..., alias="pinch_roll")
    strRoll: float = Field(..., alias="str_roll")
    horsepowerRequired: float = Field(..., alias="horsepower_required")
    actualCoilWeight: float = Field(..., alias="actual_coil_weight")
    coilOD: float = Field(..., alias="coil_od")
    strTorque: float = Field(..., alias="str_torque")
    accelerationTorque: float = Field(..., alias="acceleration_torque")
    brakeTorque: float = Field(..., alias="brake_torque")

@router.post("/calculate")
def calculate_str_utility(data: StrUtilityInput):
    # Lookups for calculations
    try:
        str_roll_dia = get_str_roll_dia(data.str_model)
        center_dist = get_center_dist(data.str_model)
        pinch_roll_dia = get_pinch_roll_dia(data.str_model)
        jack_force_available = get_jack_force_available(data.str_model)
        max_roll_depth = get_max_roll_depth(data.str_model)
        density = get_material_density(data.material_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Needed values for calculations
    if data.selected_roll.startswith("7"):
        str_qty = 7
    elif data.selected_roll.startswith("9"):
        str_qty = 9
    else:
        str_qty = 11

    if str_qty < 7:
        k_cons = (str_qty / 3.5) + 0.1
    elif str_qty < 9:
        k_cons = str_qty / 3.5
    elif str_qty < 11:
        k_cons = (str_qty / 3.5) - 0.1
    else:
        k_cons = 3

    motor_rpm = 1750
    eff = 0.85
    coil_od_min = 72

    # Required Force
    required_force = ((16 * data.yield_strength * data.coil_id * (data.thickness ** 2) / (15 * center_dist))
                    + (16 * data.yield_strength * data.coil_width * (data.thickness ** 2) / (15 * center_dist)))

    # Pinch Roll
    str_torque = (((((((0.667 * data.yield_strength * data.coil_width * (data.thickness ** 2)) / center_dist) * 0.35 * data.feed_rate * k_cons) / 33000) * 5250) / motor_rpm) * 12) / eff
    
    coil_od_measured = sqrt((data.coil_id ** 2) + ((data.coil_weight_cap * 4) / (pi * density * data.coil_width)))
    coil_od = coil_od_min if coil_od_measured < coil_od_min else coil_od_measured
    brake_torque = (((((())))))

    pinch_ratio = motor_rpm / ((data.feed_rate * 12) / (pinch_roll_dia * pi))
    min_od_brake_torque = 0

    return {
        "required_force": 0,
        "pinch_roll" : 0,
        "str_roll": 0,
        "horsepower_required": 0,
        "actual_coil_weight" : 0,
        "coil_od" : 0,
        "str_torque" : 0,
        "acceleration_torque" : 0,
        "brake_torque" : 0
    }

@router.post("/lookup")
def lookup_str_utility(data: Lookups):
    # Lookups
    
    return {
        "str_roll_dia" : 0,
        "pinch_roll_dia" : 0,
        "center_dist" : 0,
        "jack_force_available" : 0,
        "max_roll_depth" : 0,
        "modulus" : 0,
        "pinch_roll_gear_teeth" : 0,
        "pinch_roll_gear_dp" : 0,
        "str_roll_gear_teeth" : 0,
        "str_roll_gear_dp" : 0,
        "face_width_teeth" : 0,
        "cont_angle_teeth" : 0
    }