from fastapi import HTTPException
from pydantic import BaseModel
from math import sqrt, floor

class TimeInput(BaseModel):
    acceleration: float
    application: str
    feed_angle_1: float
    feed_angle_2: float
    frictional_torque: float
    increment: float
    loop_torque: float
    match: float

    min_length: float
    motor_inertia: float
    motor_rms_torque: float
    motor_peak_torque: float

    ratio: float
    efficiency: float
    refl_inertia: float
    rpm: float
    settle_time: float
    settle_torque: float

    str_max_sp: float
    str_max_sp_inch: float
    velocity: float
    width: float
    material_width: float
    material_thickness: float
    press_bed_length: float
    density: float
    material_loop: float

def calculate_init_values(data: TimeInput, feed_angle: int = 0):
    """
    Calculate initial values based on the input data.
    """
    # initial calculations
    length = ((data.velocity / data.acceleration) * data.velocity) * 12
    acceleration_time = data.velocity / data.acceleration
    acceleration_torque = (((data.refl_inertia * data.rpm) / (9.55 * acceleration_time)) / data.efficiency) + ((data.motor_inertia * data.rpm) / (9.55 * acceleration_time))
    peak_torque = acceleration_torque + data.frictional_torque + data.loop_torque

    if (length - ((data.motor_peak_torque * acceleration_time)) / 12) / data.motor_peak_torque > 0:
        runtime = ((length - ((data.motor_peak_torque * acceleration_time) * 12)) / 12) / data.motor_peak_torque
    else:
        runtime = 0
    
    index_time = ((acceleration_time * 2) + runtime + data.settle_time)
    if data.application.lower() == "y" or data.application.lower() == "yes":
        cycle_time = index_time * (360 / feed_angle)
    else:
        cycle_time = index_time + feed_angle

    strokes_per_minute = 60 / cycle_time
    dwell_time = cycle_time - index_time
    rms_torque = sqrt((((peak_torque ** 2) * acceleration_time) + 
                       ((acceleration_torque ** 2) * acceleration_time) + 
                       (((data.frictional_torque + data.loop_torque) ** 2) * runtime) + 
                       ((data.settle_torque ** 2) * data.settle_time) + 
                       ((data.loop_torque ** 2) * dwell_time)) / cycle_time)
    
    return {
        "init_length": length,
        "init_acceleration_time": acceleration_time,
        "init_acceleration_torque": acceleration_torque,
        "init_peak_torque": peak_torque,
        "init_runtime": runtime,
        "init_index_time": index_time,
        "init_cycle_time": cycle_time,
        "init_strokes_per_minute": strokes_per_minute,
        "init_dwell_time": dwell_time,
        "init_rms_torque": rms_torque
    }

def calculate_values(data: TimeInput, init_values: dict, feed_angle: int = 0, index: int = 1):
    """
    Calculate shorter values based on the initial values and input data.
    """
    # Calculate shorter values
    if index == 1:
        length = data.min_length
    else:
        length = data.min_length + (data.increment * (index - 1))

    if length > init_values["init_length"]:
        acceleration_time = init_values["init_acceleration_time"]
        runtime = ((length - init_values["init_length"]) / 12 ) / data.velocity
    else:
        acceleration_time = sqrt((length / 12) / data.acceleration)
        runtime = 0

    acceleration_torque = (((data.refl_inertia * data.rpm) / (9.55 * acceleration_time)) / data.efficiency) + ((data.motor_inertia * data.rpm) / (9.55 * acceleration_time))
    peak_torque = acceleration_torque + data.frictional_torque + data.loop_torque

    index_time = (acceleration_time * 2) + runtime + data.settle_time
    if data.application.lower() == "y" or data.application.lower() == "yes":
        cycle_time = index_time * (360 / feed_angle)
    else:
        cycle_time = index_time + feed_angle

    dwell_time = cycle_time - index_time
    rms_torque = sqrt((((peak_torque ** 2) * acceleration_time) + 
                       ((acceleration_torque ** 2) * acceleration_time) + 
                       (((data.frictional_torque + data.loop_torque) ** 2) * runtime) + 
                       ((data.settle_torque ** 2) * data.settle_time) + 
                       ((data.loop_torque ** 2) * dwell_time)) / cycle_time)
    
    if 60 / cycle_time * length < data.str_max_sp_inch:
        strokes_per_minute = floor(60 / cycle_time)
    else: 
        strokes_per_minute = floor(data.str_max_sp_inch / length)

    return {
        "length": length,
        "acceleration_time": acceleration_time,
        "acceleration_torque": acceleration_torque,
        "peak_torque": peak_torque,
        "runtime": runtime,
        "index_time": index_time,
        "cycle_time": cycle_time,
        "strokes_per_minute": strokes_per_minute,
        "dwell_time": dwell_time,
        "rms_torque": rms_torque
    }

def calculate_feed_time(data: TimeInput, feed_angle: int = 0):
    """
    Calculate the feed time based on the input data.
    """
    init_values = calculate_init_values(data, feed_angle)
    min_values = calculate_values(data, init_values, feed_angle, 1)

    lengths = [{
        "index": 0,
        "length": init_values["init_length"],
        "acceleration_time": init_values["init_acceleration_time"],
        "acceleration_torque": init_values["init_acceleration_torque"],
        "peak_torque": init_values["init_peak_torque"],
        "runtime": init_values["init_runtime"],
        "index_time": init_values["init_index_time"],
        "cycle_time": init_values["init_cycle_time"],
        "strokes_per_minute": init_values["init_strokes_per_minute"],
        "dwell_time": init_values["init_dwell_time"],
        "rms_torque": init_values["init_rms_torque"]
    },
    {
        "index": 1,
        "length": min_values["length"],
        "acceleration_time": min_values["acceleration_time"],
        "acceleration_torque": min_values["acceleration_torque"],
        "peak_torque": min_values["peak_torque"],
        "runtime": min_values["runtime"],
        "index_time": min_values["index_time"],
        "cycle_time": min_values["cycle_time"],
        "strokes_per_minute": min_values["strokes_per_minute"],
        "dwell_time": min_values["dwell_time"],
        "rms_torque": min_values["rms_torque"]
    }]

    for i in range(2, 22):
        values = calculate_values(data, init_values, data.feed_angle_1, i)
        lengths.append({
            "index": i,
            "length": values["length"],
            "acceleration_time": values["acceleration_time"],
            "acceleration_torque": values["acceleration_torque"],
            "peak_torque": values["peak_torque"],
            "runtime": values["runtime"],
            "index_time": values["index_time"],
            "cycle_time": values["cycle_time"],
            "strokes_per_minute": values["strokes_per_minute"],
            "dwell_time": values["dwell_time"],
            "rms_torque": values["rms_torque"]
        })

    return lengths

def calculate_time(data: TimeInput):
    try:
        feed_angle_1_values = calculate_feed_time(data, data.feed_angle_1)
        feed_angle_2_values = calculate_feed_time(data, data.feed_angle_2)

        return {
            "feed_angle_1": feed_angle_1_values,
            "feed_angle_2": feed_angle_2_values
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))