from fastapi import APIRouter
from ..services.feed_calculations import (
    run_allen_bradley_calculation, AllenBradleyInput
)

router = APIRouter()

@router.post("/calculate")
def calculate_allen_bradley(data: AllenBradleyInput):
    result = run_allen_bradley_calculation(data, "allen_bradley")
    return result
