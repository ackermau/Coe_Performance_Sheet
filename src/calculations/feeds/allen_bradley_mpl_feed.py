"""
Allen Bradley MPL Feed Module

"""
from services.feed_calculations import run_allen_bradley_calculation
from models import AllenBradleyInput
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import rfq_state, JSON_FILE_PATH
from pydantic import BaseModel

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
            data={rfq_state.reference: result},
            reference_number=rfq_state.reference,
            directory=JSON_FILE_PATH
        )
    except:
        return "ERROR: Allen Bradley calculations failed to save."

    return result
