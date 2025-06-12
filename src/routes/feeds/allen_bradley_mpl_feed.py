"""
Allen Bradley MPL Feed Module

"""

from fastapi import APIRouter
from services.feed_calculations import run_allen_bradley_calculation
from models import AllenBradleyInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH

# Initialize FastAPI router
router = APIRouter()

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

@router.get("/load")
def load_allen_bradley():
    """
    Load previously calculated Allen Bradley MPL feed data.
    
    Returns: \n
        dict: A dictionary containing the count and entries of the loaded data.
        If no data is found, returns an empty list with count 0.
        If an error occurs, returns an error message.
    
    """

    try:
        data = load_json_list(label="load_allen_bradley", reference_number=rfq_state.reference, directory=JSON_FILE_PATH)
        return {"count": len(data), "entries": data}
    except FileNotFoundError:
        return {"count": 0, "entries": []}
    except Exception as e:
        return {"error": str(e)}