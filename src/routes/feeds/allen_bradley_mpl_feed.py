"""
Allen Bradley MPL Feed Module

"""

from fastapi import APIRouter, Body, HTTPException
from services.feed_calculations import run_allen_bradley_calculation
from models import AllenBradleyInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH
from pydantic import BaseModel

# Initialize FastAPI router
router = APIRouter()

# In-memory storage for Allen Bradley MPL feed
local_allen_bradley_feed: dict = {}

class AllenBradleyFeedCreate(BaseModel):
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
def calculate_allen_bradley(data: AllenBradleyInput):
    """
    Calculate Allen Bradley MPL feed parameters.

    Args: \n
        data (AllenBradleyInput): Input data containing feed parameters.

    Returns: \n
        dict: A dictionary containing calculated feed parameters.

    Raises: \n
        Exception: If an error occurs during the calculation or saving process.

    """
    result = run_allen_bradley_calculation(data, "allen_bradley")

    # Save the result to a JSON file
    try:
        append_to_json_list(
            label="load_allen_bradley", 
            reference_number=rfq_state.reference, 
            data=result, 
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        return {"error": str(e)}

    return result

@router.post("/{reference}")
def create_allen_bradley_feed(reference: str, feed: AllenBradleyFeedCreate = Body(...)):
    """
    Create and persist a new Allen Bradley MPL feed entry for a given reference.
    Sets the shared rfq_state to the reference, stores in memory, and appends to JSON file.
    """
    try:
        if not reference or not reference.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")
        # Store in memory
        local_allen_bradley_feed[reference] = feed.dict(exclude_unset=True)
        # Update shared state
        rfq_state.reference = reference
        # Prepare for persistence
        current_feed = {reference: feed.dict(exclude_unset=True)}
        try:
            append_to_json_list(
                label="allen_bradley_feed",
                data=current_feed,
                reference_number=reference,
                directory=JSON_FILE_PATH
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save Allen Bradley Feed: {str(e)}")
        return {"message": "Allen Bradley Feed created", "allen_bradley_feed": feed.dict(exclude_unset=True)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{reference}")
def load_allen_bradley_feed_by_reference(reference: str):
    """
    Retrieve Allen Bradley Feed by reference number (memory first, then disk).
    """
    feed_from_memory = local_allen_bradley_feed.get(reference)
    if feed_from_memory:
        return {"allen_bradley_feed": feed_from_memory}
    try:
        feed_data = load_json_list(
            label="allen_bradley_feed",
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if feed_data:
            return {"allen_bradley_feed": feed_data}
        else:
            return {"error": "Allen Bradley Feed not found"}
    except FileNotFoundError:
        return {"error": "Allen Bradley Feed file not found"}
    except Exception as e:
        return {"error": f"Failed to load Allen Bradley Feed: {str(e)}"}
    