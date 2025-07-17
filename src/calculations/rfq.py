""" 
Request for Quote (RFQ) Management Module

"""
from models import RFQ, FPMInput
from typing import Dict, Optional
from utils.shared import rfq_state, JSON_FILE_PATH
from utils.database import get_default_db
from datetime import datetime
from pydantic import BaseModel

# Initialize the database connection (move credentials to env/config in production)
db = get_default_db()

# Global in-memory RFQ storage
current_rfq: Dict[str, RFQ] = {}
local_rfqs: Dict[str, RFQ] = {}
reference: str = ""

class RFQCreate(BaseModel):
    """Model for creating a new RFQ with optional fields"""
    date: Optional[str] = None
    version: Optional[str] = None
    customer: Optional[str] = None
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
    coil_width_max: Optional[float] = None
    coil_width_min: Optional[float] = None
    max_coil_od: Optional[float] = None
    coil_id: Optional[float] = None
    coil_weight_max: Optional[float] = None
    coil_handling_cap_max: Optional[float] = None
    type_of_coil: Optional[str] = None
    coil_car: Optional[bool] = None
    run_off_backplate: Optional[bool] = None
    req_rewinding: Optional[bool] = None
    # Material specifications (single version)
    material_thickness: Optional[float] = None
    material_width: Optional[float] = None
    material_type: Optional[str] = None
    yield_strength: Optional[float] = None
    tensile_strength: Optional[float] = None
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

