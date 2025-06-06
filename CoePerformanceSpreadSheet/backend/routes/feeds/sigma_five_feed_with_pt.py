from fastapi import APIRouter
from ..services.feed_calculations import run_sigma_five_calculation, run_sigma_five_pt_calculation, FeedWPullThruInput

router = APIRouter()

@router.post("/calculate")
def calculate_sigma_five_pt(data: FeedWPullThruInput):

    base_result = run_sigma_five_calculation(data, "sigma_five_pt")
    pt_result = run_sigma_five_pt_calculation(base_result, 
                data.straightening_rolls, data.material_width, data.material_thickness, 
                data.feed_model, data.yield_strength, data.str_pinch_rolls, data.req_max_fpm, "sigma_five_pt")
    
    base_result["peak_torque"] += pt_result["straightner_torque"]

    result = base_result | pt_result

    return result