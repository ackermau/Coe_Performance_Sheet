from fastapi import APIRouter
from ..services.feed_calculations import run_sigma_five_calculation
from models import FeedInput

router = APIRouter()

@router.post("/calculate")
def calculate_sigma_five(data: FeedInput):
    result = run_sigma_five_calculation(data, "sigma_five")
    return result
