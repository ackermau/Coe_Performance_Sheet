
""" 
Request for Quote (RFQ) Management Module

"""

from fastapi import APIRouter, Body
from models import RFQ, FPMInput
from typing import Dict
from utils.shared import rfq_state, JSON_FILE_PATH
from utils.json_util import append_to_json_list, load_json_list

# Initialize FastAPI router
router = APIRouter()

# Global in-memory RFQ storage
current_rfq: Dict[str, RFQ] = {}
local_rfqs: Dict[str, RFQ] = {}
reference: str = ""

@router.post("/")
def create_rfq(rfq: RFQ):
    """
    Create and persist a new RFQ entry.

    Sets the shared rfq_state to the new RFQ, stores it in memory,
    and appends the RFQ data to a JSON file for persistence.

    Args: \n
        rfq (RFQ): The input RFQ object containing:
            - reference: Unique identifier for the RFQ
            - company_name: Name of the requesting company
            - date: RFQ date

    Returns: \n
        Dict[str, Any]: 
            - On success: {"message": "RFQ created", "rfq": rfq}
            - On error: {"error": "error message"}
    """

    # Update shared RFQ state
    rfq_state.reference = rfq.reference
    rfq_state.company_name = rfq.company_name
    rfq_state.date = rfq.date

    # Store RFQ in memory for fast access
    local_rfqs[rfq.reference] = rfq

    # Create a dictionary for persistence
    current_rfq = Dict[rfq.reference, rfq]

    # Save the RFQ to JSON file storage
    try:
        append_to_json_list(
            label="rfq", 
            data=current_rfq, 
            reference=rfq.reference, 
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        return {"error": f"Failed to save RFQ: {str(e)}"}

    return {"message": "RFQ created", "rfq": rfq}

@router.get(f"/{reference}")
def load_rfq():
    """
    Retrieve an RFQ by its reference number.

    Checks in-memory RFQ storage first. If not found, attempts to
    load the RFQ from disk-based JSON storage.

    Args: \n
        reference (str): Reference number of the RFQ

    Returns: \n
        Dict[str, Any]: 
            - On success: {"rfq": rfq}
            - If not found: {"error": "RFQ not found"}
            - If file errors: {"error": "error message"}
    """

    # First, attempt to retrieve from memory
    rfq_from_memory = local_rfqs.get(reference)
    if rfq_from_memory:
        return {"rfq": rfq_from_memory}

    # Attempt to retrieve from disk
    try:
        rfq_data = load_json_list(
            label="rfq", 
            reference_number=reference, 
            directory=JSON_FILE_PATH
        )
        if rfq_data:
            return {"rfq": rfq_data}
        else:
            return {"error": "RFQ not found"}
    except FileNotFoundError:
        return {"error": "RFQ file not found"}
    except Exception as e:
        return {"error": f"Failed to load RFQ: {str(e)}"}

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
