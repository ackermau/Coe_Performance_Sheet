"""
Sigma Five Feed Module

"""
from services.feed_calculations import run_sigma_five_calculation
from models import FeedInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH
from pydantic import BaseModel

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
    except:
        return "ERROR: Sigma 5 calculations failed to save."

    return result
