from fastapi import APIRouter
from models import MachineSpec
from typing import Dict

router = APIRouter()

db_machines: Dict[int, MachineSpec] = {}
next_machine_id = 1

@router.post("/")
def add_machine(machine: MachineSpec):
    global next_machine_id
    db_machines[next_machine_id] = machine
    next_machine_id += 1
    return {"message": "Machine added", "machine": machine}

@router.get("/{machine_id}")
def get_machine(machine_id: int):
    return db_machines.get(machine_id, {"error": "Machine not found"})
