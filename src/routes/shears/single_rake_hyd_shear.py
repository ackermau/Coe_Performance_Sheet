"""
Single Rake Hyd Shear Calculation Module

"""

from fastapi import APIRouter
from services.hyd_shear_calculations import calculate_hyd_shear
from models import HydShearInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH

# Initialize FastAPI router
router = APIRouter()

@router.post("/calculate")
def calculate_single_rake_hyd_shear(data: HydShearInput, spec_type: str = "single_rake"):
    """
    Calculate hydraulic shear parameters for a single rake shear.

    Args: \n
        data (HydShearInput): Input data containing shear parameters.
        spec_type (str): Type of shear specification, either "single_rake" or "bow_tie".

    Returns: \n
        dict: A dictionary containing calculated shear parameters.

    Raises: \n
        ValueError: If the spec_type is not recognized.

    """
    
    results = calculate_hyd_shear(data, spec_type)

    # Save the result to a JSON file
    try:
        append_to_json_list(
            label="load_single_rake_hyd_shear", 
            reference_number=rfq_state.reference, 
            data=results, 
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        return {"error": str(e)}

    return results

@router.get("/load")
def load_single_rake_hyd_shear():
    """
    Load previously calculated single rake hydraulic shear data.
    
    Returns: \n
        dict: A dictionary containing the count and entries of the loaded data.
        If no data is found, returns an empty list with count 0.
        If an error occurs, returns an error message.

    """

    try:
        data = load_json_list(label="load_single_rake_hyd_shear", reference_number=rfq_state.reference, directory=JSON_FILE_PATH)
        return {"count": len(data), "entries": data}
    except FileNotFoundError:
        return {"count": 0, "entries": []}
    except Exception as e:
        return {"error": str(e)}