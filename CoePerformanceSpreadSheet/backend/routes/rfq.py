from fastapi import APIRouter, Body
from models import RFQ, MachineSpec
from typing import Dict

router = APIRouter()

db_rfqs: Dict[int, RFQ] = {}
next_id = 1

@router.post("/")
def create_rfq(rfq: RFQ):
    global next_id
    rfq.id = next_id
    db_rfqs[next_id] = rfq
    next_id += 1
    return {"message": "RFQ created", "rfq": rfq}

@router.get("/{rfq_id}")
def get_rfq(rfq_id: int):
    return db_rfqs.get(rfq_id, {"error": "RFQ not found"})


@router.post("/calculate_fpm")
def calculate_fpm(feed_length: float = Body(...), spm: float = Body(...)):
    if feed_length > 0 and spm > 0:
        fpm = round((feed_length * spm) / 12, 2)
        return {"fpm": fpm}
    return {"fpm": ""}