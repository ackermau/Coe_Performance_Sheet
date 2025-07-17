"""
Sigma Five Feed with Pull Thru Calculation Module

"""
from services.feed_calculations import run_sigma_five_calculation, run_sigma_five_pt_calculation
from models import FeedWPullThruInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH
from pydantic import BaseModel

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
            data={rfq_state.reference: result},
            reference_number=rfq_state.reference,
            directory=JSON_FILE_PATH
        )
    except:
        return "ERROR: Sigma 5 with pull thru calculations failed to save."

    return result
