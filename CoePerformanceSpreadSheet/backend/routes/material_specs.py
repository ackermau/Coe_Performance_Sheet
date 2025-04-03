from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class MaterialSpecsPayload(BaseModel):
    materialType: str = None
    materialWidth: float = None
    materialThickness: float = None
    yieldStrength: float = None
    # Add other fields you need for calculations

@router.post("/material/calculate")
def calculate_specs(payload: MaterialSpecsPayload):
    # Example calculation logic (secure and private)
    return {
        "coilODCalculatedMax": round((payload.materialWidth or 0) * 1.25, 2),
        "requiredMaxFPMMax": round((payload.yieldStrength or 0) * 0.42, 2)
        # Return whatever fields you calculate
    }
