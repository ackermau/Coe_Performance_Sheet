from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field
from math import pi, sqrt

# Import your lookup functions
from .utils.lookup_tables import get_material_density, get_reel_max_weight, get_friction

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
    coil_weight: Optional[float] = None
    # Will override density and max_weight if not provided.
    density: Optional[float] = None  
    max_weight: Optional[float] = None  

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

    # For lookup: note the field name expected is materialType (with a capital T)
    materialType: str
    reel_model: str

class TDDBHDOutput(BaseModel):
    webTensionPsi: float = Field(..., alias="web_tension_psi")
    webTensionLbs: float = Field(..., alias="web_tension_lbs")
    coilWeight: float = Field(..., alias="coil_weight")
    coilOd: float = Field(..., alias="coil_od")
    dispReelMtr: float = Field(..., alias="disp_reel_mtr")
    torqueAtMandrel: Optional[float] = Field(None, alias="torque_at_mandrel")
    rewindTorque: float = Field(..., alias="rewind_torque")
    holdDownForceRequired: float = Field(..., alias="hold_down_force_required")
    holdDownForceAvailable: float = Field(..., alias="hold_down_force_available")
    minMaterialWidth: float = Field(..., alias="min_material_width")
    torqueRequired: float = Field(..., alias="torque_required")
    failsafeDoubleStage: float = Field(..., alias="failsafe_double_stage")
    failsafeHoldingForce: float = Field(..., alias="failsafe_holding_force")

    class Config:
        allow_population_by_field_name = True

@router.post("/calculate")
def calculate_tbdbhd(data: TDDBHDInput):
    # Override density & max_weight using lookup if missing
    try:
        density_lookup = get_material_density(data.materialType)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        reel_max_weight = get_reel_max_weight(data.reel_model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        friction_lookup = get_friction()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    density = density_lookup
    max_weight = reel_max_weight
    friction = friction_lookup

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
    disp_reel_mtr = {22: 22.6, 38: 38, 60: 60}.get(int(data.drive_torque or 0), data.drive_torque)

    # 5. Torque At Mandrel
    torque_at_mandrel = (data.drive_torque if data.type_of_line.upper() == "PULLOFF" 
                          else data.reel_drive_tqempty)

    # 6. Rewind Torque Calculation
    rewind_torque = web_tension_lbs * coil_od / 2

    # 7. Holddown Pressure
    if "psi air" in data.holddown_matrix_label.lower():
        holddown_pressure = min(data.air_pressure, data.max_psi)
    else:
        holddown_pressure = data.air_pressure

    # 8. Holddown Force Required Calculation
    # Denom for hold down force: friction * (coil_id/2)
    hold_down_denominator = friction * (data.coil_id / 2)
    if hold_down_denominator == 0:
        raise HTTPException(status_code=400, detail="Friction and coil_id must be non-zero for hold down force calculation.")

    # Additional check for thickness in the else clause:
    if data.M >= data.My and data.thickness == 0:
        raise HTTPException(status_code=400, detail="Thickness must be non-zero for hold down force calculation.")

    if data.M < data.My:
        hold_down_force_req = data.M / hold_down_denominator
    else:
        hold_down_force_req = (
            ((data.width * data.thickness**2) * data.yield_strength *
             (1 - (1/3) * (data.y / (data.thickness / 2))**2)) /
            hold_down_denominator
        )

    # 9. Holddown Force Available
    hold_down_force_available = data.holddown_force_factor * holddown_pressure

    # 10. Torque Required Calculation
    # Check that coil_od isn't zero.
    if coil_od == 0:
        raise HTTPException(status_code=400, detail="Calculated coil OD must be non-zero for torque calculation.")
    torque_required = ((3 * data.decel * coil_weight * (coil_od**2 + data.coil_id**2)) / (386 * coil_od)) + data.tension_torque

    # 11. Failsafe: Double Stage
    if data.brake_qty == 0:
        raise HTTPException(status_code=400, detail="Brake quantity must be non-zero for failsafe calculation.")
    failsafe_double_stage = data.press_force_required / data.brake_qty

    # 12. Failsafe Holding Force
    failsafe_holding_force = (
        data.press_force_holding * friction *
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
