from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from math import pi, sqrt
from typing import Optional

from .utils.lookup_tables import (
    get_reel_dimensions,
    get_material,
    get_motor_inertia,
    get_type_of_line,
    get_fpm_buffer
)

router = APIRouter()

class ReelDriveInput(BaseModel):
    model: str
    material_type: str
    coil_weight: float
    coil_id: float
    coil_od: float
    reel_width: float
    backplate_diameter: float
    motor_hp: float
    type_of_line: str
    required_max_fpm: float

@router.post("/calculate")
def calculate_reeldrive(data: ReelDriveInput):
    # Lookups
    try:
        reel = get_reel_dimensions(data.model)
        material = get_material(data.material_type)
        if (data.motor_hp == 7.5) :
            motor_inertia = get_motor_inertia(str(data.motor_hp))
        else:
            motor_inertia = get_motor_inertia(str(int(data.motor_hp)))
        reel_type = get_type_of_line(data.type_of_line)
        fpm_buffer = get_fpm_buffer("DEFAULT")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Constants
    chain_ratio = 4
    chain_sprkt_od = 31
    chain_sprkt_thickness = 1.3
    reducer_driving = 0.85
    reducer_backdriving = 0.5
    reducer_inertia = 0.1
    motor_base_rpm = 1750
    accel_rate = 1

    # Speed and Accel Time
    speed = data.required_max_fpm * fpm_buffer
    accel_time = speed / 60 / accel_rate

    # Total Ratio
    mandrel_max_rpm = speed * 12 / data.coil_id / pi
    mandrel_full_rpm = speed * 12 / data.coil_od / pi
    total_ratio = motor_base_rpm / mandrel_max_rpm

    # Reel
    reel_size = reel["coil_weight"]
    brg_dist = reel["bearing_dist"]
    f_brg_dia = reel["fbearing_dia"]
    r_brg_dia = reel["rbearing_dia"]

    # Mandrel
    mandrel_dia = reel["mandrel_dia"]
    mandrel_length = data.reel_width + 17 + brg_dist
    mandrel_weight = ((mandrel_dia/2)**2) * pi * mandrel_length * 0.283
    mandrel_inertia = mandrel_weight / 32.3 / 2 * ((mandrel_dia/2)**2 / 144) * 12
    mandrel_refl = mandrel_inertia / total_ratio**2

    # Backplate
    backplate_weight = ((data.backplate_diameter/2)**2) * pi * 0.283
    backplate_inertia = backplate_weight / 32.3 / 2 * ((mandrel_dia/2)**2 / 144) * 12
    backplate_refl = backplate_inertia / total_ratio**2

    # Coil
    coil_density = material["density"]
    coil_width = data.coil_weight / coil_density / ((data.coil_od**2 + data.coil_id**2)/4) / pi
    coil_inertia = data.coil_weight / 32.3 / 2 * ((data.coil_od/2)**2 + (data.coil_id/2)**2) /144 * 12
    coil_refl = coil_inertia / total_ratio**2

    # Reducer
    reducer_ratio = total_ratio / chain_ratio

    # Chain
    chain_weight = ((chain_sprkt_od/2)**2) * pi * chain_sprkt_thickness * 0.283
    chain_inertia = chain_weight / 32.3 / 2 * ((chain_sprkt_od/2)**2 / 144) * 12
    chain_refl = chain_inertia / total_ratio**2

    # Totals
    total_refl_empty = mandrel_refl + backplate_refl + reducer_inertia + chain_refl
    total_refl_full = total_refl_empty + coil_refl

    # Motor RPM Full
    motor_rpm_full = speed * 12 / data.coil_od / pi * total_ratio

    # Friction
    friction_arm = (data.reel_width / 2) + 13
    r_brg_mand = mandrel_weight * friction_arm / brg_dist * 0.002 * r_brg_dia / 2
    f_brg_mand = (mandrel_weight + (mandrel_weight * ((data.reel_width/2)+13) / brg_dist)) * 0.002 * f_brg_dia / 2
    r_brg_coil = data.coil_weight * friction_arm / brg_dist * 0.002 * r_brg_dia / 2
    f_brg_coil = (data.coil_weight + (data.coil_weight * ((data.reel_width/2)+13) / brg_dist)) * 0.002 * f_brg_dia / 2
    friction_total_empty = r_brg_mand + f_brg_mand
    friction_total_full = friction_total_empty + r_brg_coil + f_brg_coil
    friction_refl_empty = friction_total_empty / total_ratio / reducer_driving
    friction_refl_full = friction_total_full / total_ratio / reducer_driving

    # Torque
    torque_empty = ((((total_refl_empty * motor_base_rpm) / (9.55 * accel_time)) / reducer_driving) +
                    (motor_inertia * motor_base_rpm) / (9.55 * accel_time)) + friction_refl_empty

    torque_full = ((((total_refl_full * motor_rpm_full) / (9.55 * accel_time)) / reducer_driving) +
                   (motor_inertia * motor_rpm_full) / (9.55 * accel_time)) + friction_refl_full

    # HP Required
    hp_req_empty = torque_empty * motor_base_rpm / 63000
    hp_req_full = torque_full * motor_base_rpm / 63000
    status_empty = "valid" if data.motor_hp > hp_req_empty else "too small"
    status_full = "valid" if data.motor_hp > hp_req_full else "too small"

    # Regen
    regen_empty = ((((total_refl_empty * motor_base_rpm) / (9.55 * accel_time)) +
                   (motor_inertia * motor_base_rpm) / (9.55 * accel_time)) -
                   (friction_total_empty / total_ratio / reducer_backdriving)) * motor_base_rpm / 63000 * 746

    regen_full = ((((total_refl_full * motor_rpm_full) / (9.55 * accel_time)) +
                   (motor_inertia * motor_rpm_full) / (9.55 * accel_time)) -
                   (friction_total_full / total_ratio / reducer_backdriving)) * motor_rpm_full / 63000 * 746

    # Pulloff Recommendation
    if reel_type == "Motorized":
        if data.motor_hp > hp_req_empty and data.motor_hp > hp_req_full:
            pulloff = "OK"
        else:
            pulloff = "NOT OK"
    else:
        pulloff = "USE PULLOFF"

    return {
        "reel": {
            "size": reel_size,
            "max_width": data.reel_width,
            "brg_dist": brg_dist,
            "f_brg_dia": f_brg_dia,
            "r_brg_dia": r_brg_dia
        },
        "mandrel": {
            "diameter": mandrel_dia,
            "length": mandrel_length,
            "max_rpm": mandrel_max_rpm,
            "rpm_full": mandrel_full_rpm,
            "weight": mandrel_weight,
            "inertia": mandrel_inertia,
            "refl_inert": mandrel_refl
        },
        "backplate": {
            "diameter": data.backplate_diameter,
            "thickness": reel["backplate_thickness"],
            "weight": backplate_weight,
            "inertia": backplate_inertia,
            "refl_inert": backplate_refl
        },
        "coil": {
            "density": coil_density,
            "od": data.coil_od,
            "id": data.coil_id,
            "width": coil_width,
            "weight": data.coil_weight,
            "inertia": coil_inertia,
            "refl_inert": coil_refl
        },
        "reducer": {
            "ratio": reducer_ratio,
            "driving": reducer_driving,
            "backdriving": reducer_backdriving,
            "inertia": reducer_inertia,
            "refl_inert": reducer_inertia
        },
        "chain": {
            "ratio": chain_ratio,
            "sprkt_od": chain_sprkt_od,
            "sprkt_thk": chain_sprkt_thickness,
            "weight": chain_weight,
            "inertia": chain_inertia,
            "refl_inert": chain_refl
        },
        "total": {
            "ratio": total_ratio,
            "total_refl_inert_empty": total_refl_empty,
            "total_refl_inert_full": total_refl_full
        },
        "motor": {
            "hp": data.motor_hp,
            "inertia": motor_inertia,
            "base_rpm": motor_base_rpm,
            "rpm_full": motor_rpm_full
        },
        "friction": {
            "r_brg_mand": r_brg_mand,
            "f_brg_mand": f_brg_mand,
            "r_brg_coil": r_brg_coil,
            "f_brg_coil": f_brg_coil,
            "total_empty": friction_total_empty,
            "total_full": friction_total_full,
            "refl_empty": friction_refl_empty,
            "refl_full": friction_refl_full
        },
        "speed": {
            "speed": speed,
            "accel_rate": accel_rate,
            "accel_time": accel_time
        },
        "torque": {
            "empty": torque_empty,
            "full": torque_full
        },
        "hp_req": {
            "empty": hp_req_empty,
            "full": hp_req_full,
            "status_empty": status_empty,
            "status_full": status_full
        },
        "regen": {
            "empty": regen_empty,
            "full": regen_full
        },
        "use_pulloff": pulloff
    }
