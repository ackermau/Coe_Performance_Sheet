""" 
Request for Quote (RFQ) Management Module

"""

from fastapi import APIRouter, Body, HTTPException
from models import RFQ, FPMInput
from typing import Dict, Optional
from utils.shared import rfq_state, JSON_FILE_PATH
from utils.json_util import append_to_json_list, load_json_list
from datetime import datetime
from pydantic import BaseModel

# Initialize FastAPI router
router = APIRouter()

# Global in-memory RFQ storage
current_rfq: Dict[str, RFQ] = {}
local_rfqs: Dict[str, RFQ] = {}
reference: str = ""

class RFQCreate(BaseModel):
    """Model for creating a new RFQ with optional fields"""
    date: Optional[str] = None
    version: Optional[str] = None
    company_name: Optional[str] = None
    state_province: Optional[str] = None
    street_address: Optional[str] = None
    zip_code: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    contact_name: Optional[str] = None
    contact_position: Optional[str] = None
    contact_phone_number: Optional[str] = None
    contact_email: Optional[str] = None
    days_per_week_running: Optional[int] = None
    shifts_per_day: Optional[int] = None
    line_application: Optional[str] = None
    type_of_line: Optional[str] = None
    pull_thru: Optional[str] = None
    max_coil_width: Optional[float] = None
    min_coil_width: Optional[float] = None
    max_coil_od: Optional[float] = None
    coil_id: Optional[float] = None
    max_coil_weight: Optional[float] = None
    max_coil_handling_cap: Optional[float] = None
    type_of_coil: Optional[str] = None
    coil_car: Optional[bool] = None
    run_off_backplate: Optional[bool] = None
    req_rewinding: Optional[bool] = None
    max_material_thickness: Optional[float] = None
    max_material_width: Optional[float] = None
    max_material_type: Optional[str] = None
    max_yield_strength: Optional[float] = None
    max_tensile_strength: Optional[float] = None
    full_material_thickness: Optional[float] = None
    full_material_width: Optional[float] = None
    full_material_type: Optional[str] = None
    full_yield_strength: Optional[float] = None
    full_tensile_strength: Optional[float] = None
    min_material_thickness: Optional[float] = None
    min_material_width: Optional[float] = None
    min_material_type: Optional[str] = None
    min_yield_strength: Optional[float] = None
    min_tensile_strength: Optional[float] = None
    width_material_thickness: Optional[float] = None
    width_material_width: Optional[float] = None
    width_material_type: Optional[str] = None
    width_yield_strength: Optional[float] = None
    width_tensile_strength: Optional[float] = None
    cosmetic_material: Optional[bool] = None
    brand_of_feed_equipment: Optional[str] = None
    gap_frame_press: Optional[bool] = None
    hydraulic_press: Optional[bool] = None
    obi: Optional[bool] = None
    servo_press: Optional[bool] = None
    shear_die_application: Optional[bool] = None
    straight_side_press: Optional[bool] = None
    other: Optional[bool] = None
    tonnage_of_press: Optional[str] = None
    press_stroke_length: Optional[float] = None
    press_max_spm: Optional[float] = None
    press_bed_area_width: Optional[float] = None
    press_bed_area_length: Optional[float] = None
    window_opening_size_of_press: Optional[float] = None
    transfer_dies: Optional[bool] = None
    progressive_dies: Optional[bool] = None
    blanking_dies: Optional[bool] = None
    average_feed_length: Optional[float] = None
    average_spm: Optional[float] = None
    average_fpm: Optional[float] = None
    max_feed_length: Optional[float] = None
    max_spm: Optional[float] = None
    max_fpm: Optional[float] = None
    min_feed_length: Optional[float] = None
    min_spm: Optional[float] = None
    min_fpm: Optional[float] = None
    feed_window_degrees: Optional[float] = None
    press_cycle_time: Optional[float] = None
    voltage_required: Optional[float] = None
    space_allocated_length: Optional[float] = None
    space_allocated_width: Optional[float] = None
    obstructions: Optional[str] = None
    feeder_mountable: Optional[bool] = None
    feeder_mount_adequate_support: Optional[bool] = None
    custom_mounting: Optional[bool] = None
    passline_height: Optional[float] = None
    loop_pit: Optional[bool] = None
    coil_change_time_concern: Optional[bool] = None
    coil_change_time_goal: Optional[float] = None
    feed_direction: Optional[str] = None
    coil_landing: Optional[str] = None
    line_guard_safety_req: Optional[bool] = None
    project_decision_date: Optional[str] = None
    ideal_delivery_date: Optional[str] = None
    earliest_delivery_date: Optional[str] = None
    latest_delivery_date: Optional[str] = None
    additional_comments: Optional[str] = None

@router.post("/calculate_fpm")
def calculate_fpm(data: FPMInput):
    """
    Calculate feed speed in feet per minute (FPM).

    Args: \n
        data (FPMInput): Contains:
            - feed_length: Length of feed in inches
            - spm: Strokes per minute

    Returns: \n
        Dict[str, Union[str, float]]:
            - {"fpm": float} on success
            - {"fpm": ""} if inputs are invalid or zero
    """

    if data.feed_length > 0 and data.spm > 0:
        fpm = round((data.feed_length * data.spm) / 12, 2)
        return {"fpm": fpm}
    return {"fpm": ""}

@router.put("/{reference}")
def update_rfq(reference: str, rfq: RFQCreate = Body(...)):
    """
    Update an existing RFQ entry by reference.
    Only provided fields are updated; all other fields are preserved.
    """
    # Load existing data
    try:
        rfq_data = load_json_list(
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if not rfq_data or reference not in rfq_data:
            raise HTTPException(status_code=404, detail="RFQ not found")
        existing = rfq_data[reference]
    except Exception:
        raise HTTPException(status_code=404, detail="RFQ not found")
    # Merge updates
    updated_rfq = dict(existing)
    updated_rfq.update(rfq.dict(exclude_unset=True))
    local_rfqs[reference] = RFQ(reference=reference, **updated_rfq)
    current_rfq = {reference: updated_rfq}
    try:
        append_to_json_list(
            data=current_rfq,
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update RFQ in storage: {str(e)}"
        )
    return {"message": "RFQ updated", "rfq": updated_rfq}

@router.post("/{reference}")
def create_rfq(reference: str, rfq: RFQCreate = Body(...)):
    """
    Create and persist a new RFQ entry.

    Sets the shared rfq_state to the new RFQ, stores it in memory,
    and appends the RFQ data to a JSON file for persistence.

    Args: \n
        reference (str): The reference number for the RFQ
        rfq (RFQCreate): The input RFQ object containing optional fields

    Returns: \n
        Dict[str, Any]: 
            - On success: {"message": "RFQ created", "rfq": rfq}
            - On error: {"error": "error message"}
    """
    try:
        # Validate reference number
        if not reference or not reference.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")

        # Create a new RFQ instance with the reference from the URL
        new_rfq = RFQ(reference=reference, **rfq.dict(exclude_unset=True))

        # Validate date format if provided
        if new_rfq.date:
            try:
                datetime.strptime(new_rfq.date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Date must be in YYYY-MM-DD format"
                )

        # Update shared RFQ state with provided values
        rfq_state.reference = reference
        if new_rfq.company_name:
            rfq_state.company_name = new_rfq.company_name
        if new_rfq.date:
            rfq_state.date = new_rfq.date

        # Store RFQ in memory for fast access
        local_rfqs[reference] = new_rfq

        # Create a dictionary for persistence
        current_rfq = {reference: new_rfq.dict()}

        # Save the RFQ to JSON file storage
        try:
            append_to_json_list(
                data=current_rfq,
                reference_number=reference,
                directory=JSON_FILE_PATH
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save RFQ to storage: {str(e)}"
            )

        return {"message": "RFQ created", "rfq": new_rfq.dict()}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/{reference}")
def load_rfq(reference: str):
    """
    Retrieve an RFQ by its reference number.
    """
    # First, attempt to retrieve from memory
    rfq_from_memory = local_rfqs.get(reference)
    if rfq_from_memory:
        return rfq_from_memory.dict()
    # Attempt to retrieve from disk
    try:
        rfq_data = load_json_list(
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if rfq_data and reference in rfq_data:
            return rfq_data[reference]
        else:
            raise HTTPException(status_code=404, detail="RFQ not found")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="RFQ file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load RFQ: {str(e)}")

