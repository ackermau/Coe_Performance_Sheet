"""
Single Rake Hyd Shear Calculation Module

"""
from services.hyd_shear_calculations import calculate_hyd_shear
from models import HydShearInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH
from pydantic import BaseModel

# In-memory storage for single rake hyd shear
local_single_rake_hyd_shear: dict = {}

class SingleRakeHydShearCreate(BaseModel):
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
            data={rfq_state.reference: results},
            reference_number=rfq_state.reference,
            directory=JSON_FILE_PATH
        )
    except:
        return "ERROR: Single Rake calculations failed to save."

    return results
