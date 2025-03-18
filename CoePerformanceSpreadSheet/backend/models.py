from pydantic import BaseModel
from typing import List, Dict

class MachineSpec(BaseModel):
    name: str
    type: str
    parameters: Dict[str, float]  # Inertia, regen, time, etc.

class RFQ(BaseModel):
    id: int
    customer_name: str
    project_name: str
    machines: List[MachineSpec]
