from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from math import pi, sqrt

router = APIRouter()

class TBDBHDInput(BaseModel):
    type_of_line: str
    drive_torque: Optional[float]
    reel_drive_tqempty: Optional[float]

    yield_strength: float
    thickness: float
    width: float
    coil_id: float
    coil_od: Optional[float] = None
    coil_weight: Optional[float] = None
    density: float
    max_weight: float = 60000  # lbs

    tension_torque: float
    decel: float
    y: float
    M: float
    My: float
    friction: float
    air_pressure: float
    max_psi: float
    holddown_pressure: Optional[float]
    holddown_force_factor: float
    holddown_min_width: float

    brake_qty: int
    no_brakepads: int
    brake_dist: float
    press_force_required: float
    press_force_holding: float
    holddown_matrix_label: str

@router.post("/api/tbdbhd/calculate")
def calculate_tbdbhd(data: TBDBHDInput):
    # 1. Web Tension
    web_tension_psi = data.yield_strength / 800
    web_tension_lbs = data.thickness * data.width * web_tension_psi

    # 2. Coil Weight
    cw_calc = (((data.coil_od or 0)**2 - data.coil_id**2) / 4) * pi * data.width * data.density
    coil_weight = min(cw_calc, data.max_weight)

    # 3. OD (if not provided)
    od_calc = sqrt((4 * coil_weight) / (data.density * data.width) + data.coil_id**2)
    coil_od = min(od_calc, 72) if not data.coil_od else data.coil_od

    # 4. Disp. Reel Motor (simulate map)
    disp_reel_mtr = {22: 22.6, 38: 38, 60: 60}.get(int(data.drive_torque or 0), data.drive_torque)

    # 5. Torque At Mandrel
    torque_at_mandrel = (
        data.drive_torque if data.type_of_line.upper() == "PULLOFF" else data.reel_drive_tqempty
    )

    # 6. Rewind Torque
    rewind_torque = web_tension_lbs * coil_od / 2

    # 7. Holddown Pressure
    if "psi air" in data.holddown_matrix_label.lower():
        holddown_pressure = min(data.air_pressure, data.max_psi)
    else:
        holddown_pressure = data.air_pressure

    # 8. Holddown Force Required
    if data.M < data.My:
        hold_down_force_req = data.M / (data.friction * (data.coil_id / 2))
    else:
        hold_down_force_req = (
            ((data.width * data.thickness**2) * data.yield_strength *
            (1 - (1/3)*(data.y / (data.thickness / 2))**2)) /
            (data.friction * (data.coil_id / 2))
        )

    # 9. Holddown Force Available
    hold_down_force_available = data.holddown_force_factor * holddown_pressure

    # 10. Torque Required
    torque_required = (
        (3 * data.decel * coil_weight * (coil_od**2 + data.coil_id**2)) /
        (386 * coil_od)
    ) + data.tension_torque

    # 11. Failsafe - Double Stage
    failsafe_double_stage = data.press_force_required / data.brake_qty

    # 12. Failsafe Holding Force
    failsafe_holding_force = (
        data.press_force_holding * data.friction *
        data.no_brakepads * data.brake_dist * data.brake_qty
    )

    return {
        "web_tension_psi": round(web_tension_psi, 3),
        "web_tension_lbs": round(web_tension_lbs, 3),
        "coil_weight": round(coil_weight, 3),
        "coil_od": round(coil_od, 3),
        "disp_reel_mtr": disp_reel_mtr,
        "torque_at_mandrel": round(torque_at_mandrel, 3) if torque_at_mandrel else None,
        "rewind_torque": round(rewind_torque, 3),
        "hold_down_force_required": round(hold_down_force_req, 3),
        "hold_down_force_available": round(hold_down_force_available, 3),
        "min_material_width": round(data.holddown_min_width, 3),
        "torque_required": round(torque_required, 3),
        "failsafe_double_stage": round(failsafe_double_stage, 3),
        "failsafe_holding_force": round(failsafe_holding_force, 3),
    }