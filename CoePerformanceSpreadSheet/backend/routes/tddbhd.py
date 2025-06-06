from functools import partial
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field
from math import pi, sqrt
import re

from .utils.shared import NUM_BRAKEPADS, BRAKE_DISTANCE, CYLINDER_ROD, STATIC_FRICTION

# Import your lookup functions
from .utils.lookup_tables import get_cylinder_bore, get_hold_down_matrix_label, get_material_density, get_material_modulus, get_reel_max_weight, get_pressure_psi, get_holddown_force_available, get_min_material_width, get_type_of_line, get_drive_key, get_drive_torque

router = APIRouter()

class TDDBHDInput(BaseModel):
    type_of_line: str
    reel_drive_tqempty: Optional[float]
    motor_hp: Optional[float]

    yield_strength: float
    thickness: float
    width: float
    coil_id: float
    coil_od: float
    coil_weight: float

    decel: float
    friction: float
    air_pressure: float

    brake_qty: int
    brake_model: str

    cylinder: str
    hold_down_assy: str
    hyd_threading_drive: str
    air_clutch: str
    
    # For lookup: note the field name expected is material_type (with a capital T)
    material_type: str
    reel_model: str

class TDDBHDOutput(BaseModel):
    friction: float = Field(..., alias="friction")
    webTensionPsi: float = Field(..., alias="web_tension_psi")
    webTensionLbs: float = Field(..., alias="web_tension_lbs")
    coilWeight: float = Field(..., alias="coil_weight")
    coilOd: float = Field(..., alias="coil_od")
    dispReelMtr: float = Field(..., alias="disp_reel_mtr")
    cylinderBore: float = Field(..., alias="cylinder_bore")
    torqueAtMandrel: Optional[float] = Field(None, alias="torque_at_mandrel")
    rewindTorque: float = Field(..., alias="rewind_torque")
    holddownPressure: float = Field(..., alias="holddown_pressure")
    holdDownForceRequired: float = Field(..., alias="hold_down_force_required")
    holdDownForceAvailable: float = Field(..., alias="hold_down_force_available")
    minMaterialWidth: float = Field(..., alias="min_material_width")
    torqueRequired: float = Field(..., alias="torque_required")
    brakePressRequired: float = Field(..., alias="brake_press_required")
    brakePressHoldingForce: float = Field(..., alias="failsafe_holding_force")

    class Config:
        allow_population_by_field_name = True

@router.post("/calculate")
def calculate_tbdbhd(data: TDDBHDInput):
    num_brakepads = NUM_BRAKEPADS
    brake_dist = BRAKE_DISTANCE
    cyl_rod = CYLINDER_ROD
    static_friction = STATIC_FRICTION

    # Lookups
    # density, max weight, friction, modulus, cylinder bore, holddown pressure, holddown force available
    try:
        density_lookup = get_material_density(data.material_type)
        reel_max_weight = get_reel_max_weight(data.reel_model)
        modulus_lookup = get_material_modulus(data.material_type)
        cylinder_bore_lookup = get_cylinder_bore(data.brake_model)
        holddown_matrix_key = get_hold_down_matrix_label(data.reel_model ,data.hold_down_assy, data.cylinder)
        holddown_pressure_calc = get_pressure_psi(holddown_matrix_key, data.air_pressure)
        holddown_matrix_key = get_hold_down_matrix_label(data.reel_model ,data.hold_down_assy, data.cylinder)
        holddown_matrix_key = get_hold_down_matrix_label(data.reel_model ,data.hold_down_assy, data.cylinder)
        min_material_width_lookup = get_min_material_width(holddown_matrix_key)
        reel_type_lookup = get_type_of_line(data.type_of_line)
        drive_key_lookup = get_drive_key(data.reel_model, data.air_clutch, data.hyd_threading_drive)
        drive_torque_lookup = get_drive_torque(drive_key_lookup)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    density = density_lookup
    max_weight = reel_max_weight
    friction = data.friction
    modulus = modulus_lookup
    cylinder_bore = cylinder_bore_lookup
    holddown_pressure = holddown_pressure_calc
    min_material_width = min_material_width_lookup
    reel_type = reel_type_lookup
    drive_torque = drive_torque_lookup

    # Precalculation for needed values
    M = (modulus * data.width * data.thickness**3) / (12 * (data.coil_id/2))
    My = (data.width * data.thickness**2 * data.yield_strength) / 6
    y = (data.thickness * (data.coil_id/2)) / (2 * ((data.thickness * modulus) / (2 * data.yield_strength)))

    # 1. Web Tension
    web_tension_psi = data.yield_strength / 800
    web_tension_lbs = data.thickness * data.width * web_tension_psi

    # 2. Coil Weight Calculation
    # Check that density and width are not zero.
    if density == 0 or data.width == 0:
        raise HTTPException(status_code=400, detail="Density and width must be non-zero for coil weight calculation.")
    calculated_cw = (((data.coil_od**2) - data.coil_id**2) / 4) * pi * data.width * density
    coil_weight = min(calculated_cw, max_weight)

    # 3. Coil OD Calculation
    try:
        od_denominator = density * data.width * pi
        if od_denominator == 0:
            raise ZeroDivisionError
        od_calc = sqrt(((4 * coil_weight) / od_denominator) + (data.coil_id**2))
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Density or width cannot be zero for OD calculation.")
    coil_od = min(od_calc, data.coil_od) 

    # 4. Display Reel Motor (simulate mapping)
    match = re.match(r"\d+", data.hyd_threading_drive)
    if not match:
        raise HTTPException(status_code=422, detail="Invalid hyd_threading_drive format. Expected to start with digits.")

    hyd_drive_number = int(match.group())
    disp_reel_mtr = {22: 22.6, 38: 38, 60: 60}.get(hyd_drive_number, hyd_drive_number)

    # 5. Torque At Mandrel
    if reel_type.upper() == "PULLOFF":
        torque_at_mandrel = drive_torque
    else: 
        torque_at_mandrel = data.reel_drive_tqempty

    # 6. Rewind Torque Calculation
    rewind_torque = web_tension_lbs * coil_od / 2

    # 8. Holddown Force Required Calculation
    # Denom for hold down force: friction * (coil_id/2)
    hold_down_denominator = static_friction * (data.coil_id / 2)
    if hold_down_denominator == 0:
        raise HTTPException(status_code=400, detail="Friction and coil_id must be non-zero for hold down force calculation.")

    # Additional check for thickness in the else clause:
    if M >= My and data.thickness == 0:
        raise HTTPException(status_code=400, detail="Thickness must be non-zero for hold down force calculation.")

    if M < My:
        hold_down_force_req = M / hold_down_denominator
    else:
        hold_down_force_req = (((data.width * data.thickness**2) / 4) * data.yield_strength * (1 - (1/3) * (y / (data.thickness / 2))**2)) / hold_down_denominator

    # 10. Torque Required Calculation
    # Check that coil_od isn't zero.
    if coil_od == 0:
        raise HTTPException(status_code=400, detail="Calculated coil OD must be non-zero for torque calculation.")
    torque_required = ((3 * data.decel * coil_weight * (coil_od**2 + data.coil_id**2)) / (386 * coil_od)) + rewind_torque

    # 11. Brake Press Required Calculation
    numerator = 4 * torque_required
    partial_denominator = pi * friction * brake_dist * num_brakepads 
    if data.brake_model == "Single Stage" or data.brake_model == "Failsafe - Single Stage":
        last = (cylinder_bore ** 2)
    elif data.brake_model == "Double Stage" or data.brake_model == "Failsafe - Double Stage":
        last = (2 * (cylinder_bore ** 2) - (cyl_rod ** 2))
    elif data.brake_model == "Triple Stage":
        last = (3 * (cylinder_bore ** 2) - 2 * (cyl_rod ** 2))
    else:
        raise HTTPException(status_code=400, detail="Invalid brake model.")

    denominator = partial_denominator * last
    press_required = numerator / denominator
    brake_press_required = press_required / data.brake_qty

    print(f"Brake Press Required: {brake_press_required}, last: {last}, numerator: {numerator}, denominator: {denominator}, cylinder_bore: {cylinder_bore}, cylinder_rod: {cyl_rod}, brake_qty: {data.brake_qty}")

    # 12. Brake Press Holding Force Calculation
    if data.brake_model == "Failsafe - Single Stage":
        hold_force = 1000
    elif data.brake_model == "Failsafe - Double Stage":
        hold_force = 2385
    else:
        hold_force = 0

    if data.brake_qty < 1 or data.brake_qty > 4:
        raise HTTPException(status_code=400, detail="Brake quantity must be between 1 and 4.")

    failsafe_holding_force = hold_force * friction * num_brakepads * brake_dist * data.brake_qty 

    return {
        "friction": round(friction, 3),
        "web_tension_psi": round(web_tension_psi, 3),
        "web_tension_lbs": round(web_tension_lbs, 3),
        "calculated_coil_weight": round(coil_weight, 3),
        "coil_od": round(coil_od, 3),
        "disp_reel_mtr": disp_reel_mtr,
        "cylinder_bore": round(cylinder_bore, 3),
        "torque_at_mandrel": round(torque_at_mandrel, 3) if torque_at_mandrel else None,
        "rewind_torque": round(rewind_torque, 3),
        "holddown_pressure": round(holddown_pressure, 3),
        "hold_down_force_required": round(hold_down_force_req, 3),
        "min_material_width": round(min_material_width, 3),
        "torque_required": round(torque_required, 3),
        "failsafe_required": round(brake_press_required, 3),
        "failsafe_holding_force": round(failsafe_holding_force, 3),
    }
