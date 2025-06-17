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
    company_name: Optional[str] = None
    date: Optional[str] = None
    # Add other optional fields as needed

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
                label="rfq", 
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
