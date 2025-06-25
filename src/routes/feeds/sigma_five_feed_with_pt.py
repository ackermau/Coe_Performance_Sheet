"""
Sigma Five Feed with Pull Thru Calculation Module

"""

from fastapi import APIRouter, Body, HTTPException
from services.feed_calculations import run_sigma_five_calculation, run_sigma_five_pt_calculation
from models import FeedWPullThruInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH
from pydantic import BaseModel

# Initialize FastAPI router
router = APIRouter()

# In-memory storage for Sigma Five feed with pull-thru
local_sigma_five_feed_pt: dict = {}

class SigmaFiveFeedWithPTCreate(BaseModel):
    feed_model: str = None
    width: int = None
    loop_pit: str = None
    material_type: str = None
    application: str = None
    type_of_line: str = None
    roll_width: str = None
    feed_rate: float = None
    material_width: int = None
    material_thickness: float = None
    press_bed_length: int = None
    friction_in_die: float = None
    acceleration_rate: float = None
    chart_min_length: float = None
    length_increment: float = None
    feed_angle_1: float = None
    feed_angle_2: float = None
    straightening_rolls: int = None
    yield_strength: float = None
    str_pinch_rolls: str = None
    req_max_fpm: float = None
    # Add other fields as needed for creation


@router.post("/{reference}")
def create_sigma_five_feed_pt(reference: str, feed: SigmaFiveFeedWithPTCreate = Body(...)):
    """
    Create and persist a new Sigma Five feed with pull-thru entry for a given reference.
    Sets the shared rfq_state to the reference, stores in memory, and appends to JSON file.
    """
    try:
        if not reference or not reference.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")
        # Store in memory
        local_sigma_five_feed_pt[reference] = feed.dict(exclude_unset=True)
        # Update shared state
        rfq_state.reference = reference
        # Prepare for persistence
        current_feed = {reference: feed.dict(exclude_unset=True)}
        try:
            append_to_json_list(
                label="sigma_five_feed_pt",
                data=current_feed,
                reference_number=reference,
                directory=JSON_FILE_PATH
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save Sigma Five Feed With PT: {str(e)}")
        return {"message": "Sigma Five Feed With PT created", "sigma_five_feed_pt": feed.dict(exclude_unset=True)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{reference}")
def load_sigma_five_feed_pt_by_reference(reference: str):
    """
    Retrieve Sigma Five Feed With PT by reference number (memory first, then disk).
    """
    feed_from_memory = local_sigma_five_feed_pt.get(reference)
    if feed_from_memory:
        return {"sigma_five_feed_pt": feed_from_memory}
    try:
        feed_data = load_json_list(
            label="sigma_five_feed_pt",
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if feed_data:
            return {"sigma_five_feed_pt": feed_data}
        else:
            return {"error": "Sigma Five Feed With PT not found"}
    except FileNotFoundError:
        return {"error": "Sigma Five Feed With PT file not found"}
    except Exception as e:
        return {"error": f"Failed to load Sigma Five Feed With PT: {str(e)}"}
    
@router.post("/calculate")
def calculate_sigma_five_pt(data: FeedWPullThruInput):
    """
    Calculate Sigma Five feed parameters with pull-thru configuration.

    Args: \n
        data (FeedWPullThruInput): Input data containing feed parameters with pull-thru.

    Returns: \n
        dict: A dictionary containing calculated feed parameters with pull-thru.

    Raises: \n
        Exception: If an error occurs during the calculation or saving process.
    
    """

    base_result = run_sigma_five_calculation(data, "sigma_five_pt")
    pt_result = run_sigma_five_pt_calculation(base_result, 
                data.straightening_rolls, data.material_width, data.material_thickness, 
                data.feed_model, data.yield_strength, data.str_pinch_rolls, data.req_max_fpm, "sigma_five_pt")
    
    base_result["peak_torque"] += pt_result["straightner_torque"]

    result = base_result | pt_result

    # Save the result to a JSON file
    try:
        append_to_json_list(
            label="load_sigma_five_pt", 
            reference_number=rfq_state.reference, 
            data=result, 
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        return {"error": str(e)}

    return result