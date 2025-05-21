from fastapi import HTTPException
from pydantic import BaseModel

class RegenInput(BaseModel):
    match: float
    motor_inertia: float
    rpm: float
    acceleration_time: float
    cycle_time: float
    watts_lost: float
    ec: float

def calculate_regen(data: RegenInput):
    try:
        # Compute rational energy of the system, es (Joules)
        motor_rotor_inertia = data.motor_inertia * 0.112943
        total_inertia = motor_rotor_inertia + data.match
        es = (total_inertia * (data.rpm ** 2)) / 182

        # calculate the energy lost in the servo motor windings, em (Joules)
        deceleration_time = data.acceleration_time
        em = deceleration_time * data.watts_lost

        # ek (resistor)
        ek = es - (em * data.ec)
        
        # Raw watts and De-rated watts (wk) calculations
        regen = ek / data.cycle_time
        wk = ek / (0.2 * data.cycle_time)

        return regen
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))