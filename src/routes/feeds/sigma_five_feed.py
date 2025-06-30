"""
Sigma Five Feed Module

"""

from fastapi import APIRouter, Body, HTTPException
from services.feed_calculations import run_sigma_five_calculation
from models import FeedInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH
from pydantic import BaseModel

# Initialize FastAPI router
router = APIRouter()

# In-memory storage for Sigma Five feed
local_sigma_five_feed: dict = {}

class SigmaFiveFeedCreate(BaseModel):
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
    # Add other fields as needed for creation

@router.post("/calculate")
def calculate_sigma_five(data: FeedInput):
    """
    Calculate Sigma Five feed parameters.

    Args: \n
        data (FeedInput): Input data containing feed parameters.

    Returns: \n
        dict: A dictionary containing calculated feed parameters.

    Raises: \n
        Exception: If an error occurs during the calculation or saving process.
    
    """

    result = run_sigma_five_calculation(data, "sigma_five")

    # Save the result to a JSON file
    try:
        append_to_json_list(
            data={rfq_state.reference: result},
            reference_number=rfq_state.reference,
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        return {"error": str(e)}

    return result

@router.put("/{reference}")
def update_sigma_five_feed(reference: str, feed: SigmaFiveFeedCreate = Body(...)):
    """
    Update an existing Sigma Five Feed entry by reference.
    Only provided fields are updated; all other fields are preserved.
    """
    # Load existing data
    try:
        feed_data = load_json_list(
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if not feed_data or reference not in feed_data:
            raise HTTPException(status_code=404, detail="Sigma Five Feed not found")
        existing = feed_data[reference]
    except Exception:
        raise HTTPException(status_code=404, detail="Sigma Five Feed not found")
    # Merge updates
    updated_feed = dict(existing)
    updated_feed.update(feed.dict(exclude_unset=True))
    local_sigma_five_feed[reference] = updated_feed
    current_feed = {reference: updated_feed}
    try:
        append_to_json_list(
            data=current_feed,
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update Sigma Five Feed in storage: {str(e)}"
        )
    return {"message": "Sigma Five Feed updated", "sigma_five_feed": updated_feed}

@router.post("/{reference}")
def create_sigma_five_feed(reference: str, feed: SigmaFiveFeedCreate = Body(...)):
    """
    Create and persist a new Sigma Five feed entry for a given reference.
    Sets the shared rfq_state to the reference, stores in memory, and appends to JSON file.
    """
    try:
        if not reference or not reference.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")
        # Store in memory
        local_sigma_five_feed[reference] = feed.dict(exclude_unset=True)
        # Update shared state
        rfq_state.reference = reference
        # Prepare for persistence
        current_feed = {reference: feed.dict(exclude_unset=True)}
        try:
            append_to_json_list(
                data=current_feed,
                reference_number=reference,
                directory=JSON_FILE_PATH
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save Sigma Five Feed: {str(e)}")
        return {"message": "Sigma Five Feed created", "sigma_five_feed": feed.dict(exclude_unset=True)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{reference}")
def load_sigma_five_feed_by_reference(reference: str):
    """
    Retrieve Sigma Five Feed by reference number (memory first, then disk).
    """
    feed_from_memory = local_sigma_five_feed.get(reference)
    if feed_from_memory:
        return feed_from_memory
    try:
        feed_data = load_json_list(
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if feed_data and reference in feed_data:
            return feed_data[reference]
        else:
            return {"error": "Sigma Five Feed not found"}
    except FileNotFoundError:
        return {"error": "Sigma Five Feed file not found"}
    except Exception as e:
        return {"error": f"Failed to load Sigma Five Feed: {str(e)}"}
