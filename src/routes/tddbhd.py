"""
TDDBHD Calculation Module

"""

from fastapi import APIRouter, HTTPException, Body
from models import TDDBHDInput
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field
from math import pi, sqrt
import re

from utils.shared import (
    NUM_BRAKEPADS, BRAKE_DISTANCE, CYLINDER_ROD, STATIC_FRICTION,
    JSON_FILE_PATH, rfq_state
)
from utils.json_util import load_json_list, append_to_json_list

# Import your lookup functions
from utils.lookup_tables import (
    get_cylinder_bore, get_hold_down_matrix_label, get_material_density, get_material_modulus, get_reel_max_weight, 
    get_pressure_psi, get_holddown_force_available, get_min_material_width, get_type_of_line, get_drive_key, get_drive_torque 
    )

# Initialize FastAPI router
router = APIRouter()

# In-memory storage for TDDBHD
local_tddbhd: dict = {}

class TDDBHDOutput(BaseModel):
    """
    TDDBHD Output Model
    """
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

class TDDBHDCreate(BaseModel):
    # Only a subset of fields for creation; adjust as needed
    type_of_line: Optional[str] = None
    reel_drive_tqempty: Optional[float] = None
    motor_hp: Optional[float] = None
    yield_strength: Optional[float] = None
    thickness: Optional[float] = None
    width: Optional[float] = None
    coil_id: Optional[float] = None
    coil_od: Optional[float] = None
    coil_weight: Optional[float] = None
    decel: Optional[float] = None
    friction: Optional[float] = None
    air_pressure: Optional[float] = None
    brake_qty: Optional[int] = None
    brake_model: Optional[str] = None
    cylinder: Optional[str] = None
    hold_down_assy: Optional[str] = None
    hyd_threading_drive: Optional[str] = None
    air_clutch: Optional[str] = None
    material_type: Optional[str] = None
    reel_model: Optional[str] = None
    reel_width: Optional[float] = None
    backplate_diameter: Optional[float] = None
    # Add other fields as needed for creation

@router.post("/calculate")
def calculate_tbdbhd(data: TDDBHDInput):
    """
    Calculate TDDBHD values based on the provided input data.

    Args: \n
        data (TDDBHDInput): Input data for TDDBHD calculations.

    Returns: \n
        TDDBHDOutput: Calculated results including web tension, coil weight, 
                      coil OD, torque required, and brake press required.

    Raises: \n
        HTTPException: If any input data is invalid or if calculations fail.

    """
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
        hold_down_force_available = get_holddown_force_available(holddown_matrix_key, data.air_pressure)
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

    # Web Tension
    web_tension_psi = data.yield_strength / 800
    web_tension_lbs = data.thickness * data.width * web_tension_psi

    # Coil Weight Calculation
    # Check that density and width are not zero.
    if density == 0 or data.width == 0:
        raise HTTPException(status_code=400, detail="Density and width must be non-zero for coil weight calculation.")
    calculated_cw = (((data.coil_od**2) - data.coil_id**2) / 4) * pi * data.width * density
    coil_weight = min(calculated_cw, max_weight)

    # Coil OD Calculation
    try:
        od_denominator = density * data.width * pi
        if od_denominator == 0:
            raise ZeroDivisionError
        od_calc = sqrt(((4 * coil_weight) / od_denominator) + (data.coil_id**2))
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Density or width cannot be zero for OD calculation.")
    coil_od = min(od_calc, data.coil_od) 

    # Display Reel Motor (simulate mapping)
    if data.hyd_threading_drive != "None":
        match = re.match(r"\d+", data.hyd_threading_drive)
        if not match:
            raise HTTPException(status_code=422, detail="Invalid hyd_threading_drive format. Expected to start with digits.")

        hyd_drive_number = int(match.group())
        disp_reel_mtr = {22: 22.6, 38: 38, 60: 60}.get(hyd_drive_number, hyd_drive_number)
    else:
        disp_reel_mtr = 0

    # Torque At Mandrel
    if reel_type.upper() == "PULLOFF":
        torque_at_mandrel = drive_torque
    else: 
        torque_at_mandrel = data.reel_drive_tqempty

    # Rewind Torque Calculation
    rewind_torque = web_tension_lbs * coil_od / 2

    # Holddown Force Required Calculation
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

    # Torque Required Calculation
    # Check that coil_od isn't zero.
    if coil_od == 0:
        raise HTTPException(status_code=400, detail="Calculated coil OD must be non-zero for torque calculation.")
    torque_required = ((3 * data.decel * coil_weight * (coil_od**2 + data.coil_id**2)) / (386 * coil_od)) + rewind_torque

    # Brake Press Required Calculation
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

    # Brake Press Holding Force Calculation
    if data.brake_model == "Failsafe - Single Stage":
        hold_force = 1000
    elif data.brake_model == "Failsafe - Double Stage":
        hold_force = 2385
    else:
        hold_force = 0

    if data.brake_qty < 1 or data.brake_qty > 4:
        raise HTTPException(status_code=400, detail="Brake quantity must be between 1 and 4.")

    failsafe_holding_force = hold_force * friction * num_brakepads * brake_dist * data.brake_qty 
    results = {
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
        "hold_down_force_available": round(hold_down_force_available, 3),
        "hold_down_force_required": round(hold_down_force_req, 3),
        "min_material_width": round(min_material_width, 3),
        "torque_required": round(torque_required, 3),
        "failsafe_required": round(brake_press_required, 3),
        "failsafe_holding_force": round(failsafe_holding_force, 3),
    }

    # Save the results to a JSON file
    try:
        append_to_json_list(
            label="tddbhd", 
            data=results, 
            reference_number=rfq_state.reference, 
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving results: {str(e)}")

    return results

@router.post("/{reference}")
def create_tddbhd(reference: str, tddbhd: TDDBHDCreate = Body(...)):
    """
    Create and persist a new TDDBHD entry for a given reference.
    Sets the shared rfq_state to the reference, stores in memory, and appends to JSON file.
    """
    try:
        if not reference or not reference.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")
        # Store in memory
        local_tddbhd[reference] = tddbhd.dict(exclude_unset=True)
        # Update shared state
        rfq_state.reference = reference
        # Prepare for persistence
        current_tddbhd = {reference: tddbhd.dict(exclude_unset=True)}
        try:
            append_to_json_list(
                label="tddbhd",
                data=current_tddbhd,
                reference_number=reference,
                directory=JSON_FILE_PATH
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save TDDBHD: {str(e)}")
        return {"message": "TDDBHD created", "tddbhd": tddbhd.dict(exclude_unset=True)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{reference}")
def load_tddbhd_by_reference(reference: str):
    """
    Retrieve TDDBHD by reference number (memory first, then disk).
    """
    tddbhd_from_memory = local_tddbhd.get(reference)
    if tddbhd_from_memory:
        return {"tddbhd": tddbhd_from_memory}
    try:
        tddbhd_data = load_json_list(
            label="tddbhd",
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if tddbhd_data:
            return {"tddbhd": tddbhd_data}
        else:
            return {"error": "TDDBHD not found"}
    except FileNotFoundError:
        return {"error": "TDDBHD file not found"}
    except Exception as e:
        return {"error": f"Failed to load TDDBHD: {str(e)}"}