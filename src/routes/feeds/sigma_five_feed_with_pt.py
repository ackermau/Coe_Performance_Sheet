"""
Sigma Five Feed with Pull Thru Calculation Module

"""

from fastapi import APIRouter
from services.feed_calculations import run_sigma_five_calculation, run_sigma_five_pt_calculation
from models import FeedWPullThruInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH

# Initialize FastAPI router
router = APIRouter()

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

@router.get("/load")
def load_sigma_five_pt():
    """
    Load previously calculated Sigma Five feed data with pull-thru configuration.

    Returns: \n
        dict: A dictionary containing the count and entries of the loaded data.
        If no data is found, returns an empty list with count 0.
        If an error occurs, returns an error message.

    Raises: \n
        FileNotFoundError: If the JSON file does not exist.
        Exception: If an error occurs while loading the data.

    """

    try:
        data = load_json_list(label="load_sigma_five_pt", reference_number=rfq_state.reference, directory=JSON_FILE_PATH)
        return {"count": len(data), "entries": data}
    except FileNotFoundError:
        return {"count": 0, "entries": []}
    except Exception as e:
        return {"error": str(e)}