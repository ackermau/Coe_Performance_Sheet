"""
Bow Tie Hyd Shear Calculations Module

"""

from fastapi import APIRouter, Body, HTTPException
from services.hyd_shear_calculations import calculate_hyd_shear
from models import HydShearInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH
from pydantic import BaseModel

# Initialize FastAPI router
router = APIRouter()

# In-memory storage for bow tie hyd shear
local_bow_tie_hyd_shear: dict = {}

class BowTieHydShearCreate(BaseModel):
    max_material_thickness: float = None
    coil_width: float = None
    material_tensile: float = None
    rake_of_blade: float = None
    overlap: float = None
    blade_opening: float = None
    percent_of_penetration: float = None
    bore_size: float = None
    rod_dia: float = None
    stroke: float = None
    pressure: float = None
    time_for_down_stroke: float = None
    dwell_time: float = None
    # Add other fields as needed for creation

@router.post("/calculate")
def calculate_bow_tie_hyd_shear(data: HydShearInput, spec_type: str = "bow_tie"):
    """
    Calculate hydraulic shear parameters for a bow tie shear.

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
            label="load_bow_tie_hyd_shear", 
            reference_number=rfq_state.reference, 
            data=results, 
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        return {"error": str(e)}
    
    return results

@router.post("/{reference}")
def create_bow_tie_hyd_shear(reference: str, shear: BowTieHydShearCreate = Body(...)):
    """
    Create and persist a new Bow Tie Hyd Shear entry for a given reference.
    Sets the shared rfq_state to the reference, stores in memory, and appends to JSON file.
    """
    try:
        if not reference or not reference.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")
        # Store in memory
        local_bow_tie_hyd_shear[reference] = shear.dict(exclude_unset=True)
        # Update shared state
        rfq_state.reference = reference
        # Prepare for persistence
        current_shear = {reference: shear.dict(exclude_unset=True)}
        try:
            append_to_json_list(
                label="bow_tie_hyd_shear",
                data=current_shear,
                reference_number=reference,
                directory=JSON_FILE_PATH
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save Bow Tie Hyd Shear: {str(e)}")
        return {"message": "Bow Tie Hyd Shear created", "bow_tie_hyd_shear": shear.dict(exclude_unset=True)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{reference}")
def load_bow_tie_hyd_shear_by_reference(reference: str):
    """
    Retrieve Bow Tie Hyd Shear by reference number (memory first, then disk).
    """
    shear_from_memory = local_bow_tie_hyd_shear.get(reference)
    if shear_from_memory:
        return {"bow_tie_hyd_shear": shear_from_memory}
    try:
        shear_data = load_json_list(
            label="bow_tie_hyd_shear",
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if shear_data:
            return {"bow_tie_hyd_shear": shear_data}
        else:
            return {"error": "Bow Tie Hyd Shear not found"}
    except FileNotFoundError:
        return {"error": "Bow Tie Hyd Shear file not found"}
    except Exception as e:
        return {"error": f"Failed to load Bow Tie Hyd Shear: {str(e)}"}
