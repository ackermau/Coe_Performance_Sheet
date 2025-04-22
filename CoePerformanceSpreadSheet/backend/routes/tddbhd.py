from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field
from math import pi, sqrt
import re

# Import your lookup functions
from .utils.lookup_tables import get_cylinder_bore, get_hold_down_matrix_label, get_material_density, get_material_modulus, get_reel_max_weight, get_friction, get_pressure_psi, get_holddown_force_available, get_min_material_width, get_press_required, get_failsafe_holding_force

router = APIRouter()

class TDDBHDInput(BaseModel):
    type_of_line: str
    drive_torque: Optional[float]
    reel_drive_tqempty: Optional[float]

    yield_strength: float
    thickness: float
    width: float
    coil_id: float
    coil_od: float
    coil_weight: float

    decel: float
    friction: float
    air_pressure: float
    max_psi: float
    holddown_pressure: Optional[float]

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
    num_brakepads = 2
    brake_dist = 12
    friction_frontend = 0.6

    # Lookups
    # density, max weight, friction, modulus, cylinder bore, holddown pressure, holddown force available
    try:
        density_lookup = get_material_density(data.material_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        reel_max_weight = get_reel_max_weight(data.reel_model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        if data.friction == 0:
            friction_lookup = get_friction()
        else:
            friction_lookup = data.friction
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        modulus_lookup = get_material_modulus(data.material_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        cylinder_bore_lookup = get_cylinder_bore(data.brake_model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        holddown_matrix_key = get_hold_down_matrix_label(data.reel_model ,data.hold_down_assy, data.cylinder)
        holddown_pressure_calc = get_pressure_psi(holddown_matrix_key, data.air_pressure)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        holddown_matrix_key = get_hold_down_matrix_label(data.reel_model ,data.hold_down_assy, data.cylinder)
        hold_down_force_available_calc = get_holddown_force_available(holddown_matrix_key, data.holddown_pressure)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        holddown_matrix_key = get_hold_down_matrix_label(data.reel_model ,data.hold_down_assy, data.cylinder)
        min_material_width_lookup = get_min_material_width(holddown_matrix_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        brake_press_required_lookup = get_press_required(data.brake_model, data.brake_qty)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        friction = get_friction()
        failsafe_holding_force_calc = get_failsafe_holding_force(data.brake_model, data.brake_qty, friction_frontend, num_brakepads, brake_dist)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    density = density_lookup
    max_weight = reel_max_weight
    friction = friction_lookup
    modulus = modulus_lookup
    cylinder_bore = cylinder_bore_lookup
    holddown_pressure = holddown_pressure_calc
    hold_down_force_available = hold_down_force_available_calc
    min_material_width = min_material_width_lookup
    brake_press_required = brake_press_required_lookup
    failsafe_holding_force = failsafe_holding_force_calc

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
        od_denominator = density * data.width
        if od_denominator == 0:
            raise ZeroDivisionError
        od_calc = sqrt((4 * coil_weight) / od_denominator + data.coil_id**2)
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Density or width cannot be zero for OD calculation.")
    coil_od = min(od_calc, data.coil_od) if not data.coil_od else data.coil_od

    # 4. Display Reel Motor (simulate mapping)
    match = re.match(r"\d+", data.hyd_threading_drive)
    if not match:
        raise HTTPException(status_code=422, detail="Invalid hyd_threading_drive format. Expected to start with digits.")

    hyd_drive_number = int(match.group())
    disp_reel_mtr = {22: 22.6, 38: 38, 60: 60}.get(hyd_drive_number, hyd_drive_number)

    # 5. Torque At Mandrel
    torque_at_mandrel = (data.drive_torque if data.type_of_line.upper() == "PULLOFF" 
                          else data.reel_drive_tqempty)

    # 6. Rewind Torque Calculation
    rewind_torque = web_tension_lbs * coil_od / 2

    # 8. Holddown Force Required Calculation
    # Denom for hold down force: friction * (coil_id/2)
    hold_down_denominator = friction * (data.coil_id / 2)
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
        "hold_down_force_available": round(hold_down_force_available, 3),
        "min_material_width": round(min_material_width, 3),
        "torque_required": round(torque_required, 3),
        "brake_press_required": round(brake_press_required, 3),
        "brake_press_holding_force": round(failsafe_holding_force, 3),
    }
