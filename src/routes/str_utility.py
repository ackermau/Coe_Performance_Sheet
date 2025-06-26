"""
Straightener Utility Calculation Module

"""

from fastapi import APIRouter, HTTPException, Body
from models import StrUtilityInput
from pydantic import BaseModel
from pydantic import Field
from math import pi, sqrt

from utils.shared import (
    MOTOR_RPM, EFFICIENCY, PINCH_ROLL_QTY, MAT_LENGTH, CONT_ANGLE, FEED_RATE_BUFFER,
    LEWIS_FACTORS, roll_str_backbend_state, rfq_state, JSON_FILE_PATH,
    get_percent_material_yielded_check
)

from utils.json_util import load_json_list, append_to_json_list

from utils.lookup_tables import (
    get_material_density, get_material_modulus, get_str_model_value, get_motor_inertia
)

# Initialize FastAPI router
router = APIRouter()

# In-memory storage for str utility
local_str_utility: dict = {}

class StrUtilityOutput(BaseModel):
    """
    Model for the output of the Straightener Utility calculations.
    """
    requiredForce: float = Field(..., alias="required_force")
    pinchRollDia: float = Field(..., alias="pinch_roll_dia")
    strRollDia: float = Field(..., alias="str_roll_dia")
    pinchRollReqTorque: float = Field(..., alias="pinch_roll_req_torque")
    pinchRollRatedTorque: float = Field(..., alias="pinch_roll_rated_torque")
    strRollReqTorque: float = Field(..., alias="str_roll_req_torque")
    strRollRatedTorque: float = Field(..., alias="str_roll_rated_torque")
    horsepowerRequired: float = Field(..., alias="horsepower_required")

    centerDist: float = Field(..., alias="center_dist")
    jackForceAvailable: float = Field(..., alias="jack_force_available")
    maxRollDepth: float = Field(..., alias="max_roll_depth")
    modulus: float = Field(..., alias="modulus")
    pinchRollTeeth: float = Field(..., alias="pinch_roll_teeth")
    pinchRollDP: float = Field(..., alias="pinch_roll_dp")
    strRollTeeth: float = Field(..., alias="str_roll_teeth")
    strRollDP: float = Field(..., alias="str_roll_dp")

    contAngle: float = Field(..., alias="cont_angle")
    faceWidth: float = Field(..., alias="face_width")
    actualCoilWeight: float = Field(..., alias="actual_coil_weight")
    coilOD: float = Field(..., alias="coil_od")
    strTorque: float = Field(..., alias="str_torque")
    accelerationTorque: float = Field(..., alias="acceleration_torque")
    brakeTorque: float = Field(..., alias="brake_torque")
    feedRateCheck: str = Field(..., alias="feed_rate_check")

class StrUtilityCreate(BaseModel):
    max_coil_weight: float = None
    coil_id: float = None
    coil_od: float = None
    coil_width: float = None
    material_thickness: float = None
    yield_strength: float = None
    material_type: str = None
    str_model: str = None
    str_width: float = None
    horsepower: float = None
    feed_rate: float = None
    max_feed_rate: float = None
    auto_brake_compensation: str = None
    acceleration: float = None
    num_str_rolls: int = None
    # Add other fields as needed for creation

@router.post("/calculate")
def calculate_str_utility(data: StrUtilityInput):
    """
    Calculate Straightener Utility values based on input data.

    Args: \n
        data (StrUtilityInput): Input data for calculations.
    
    Returns: \n
        StrUtilityOutput: Calculated values including required force, torque, horsepower, etc.
    
    Raises: \n
        HTTPException: If any input data is invalid or missing.
        ValueError: If any lookup fails or if calculations cannot be performed.
    
    """
    # Lookups for calculations
    try:
        if data.horsepower == 7.5:
            horsepower_string = "7.5"
        else:    
            horsepower_string = str(int(data.horsepower))

        str_roll_dia = get_str_model_value(data.str_model, "roll_diameter", "str_roll_dia")
        center_dist = get_str_model_value(data.str_model, "center_distance", "center_dist")
        pinch_roll_dia = get_str_model_value(data.str_model, "pinch_roll_dia", "pinch_roll_dia")
        jack_force_available = get_str_model_value(data.str_model, "jack_force_avail", "jack_force_available")
        max_roll_depth = get_str_model_value(data.str_model, "min_roll_depth", "max_roll_depth")
        str_gear_torque = get_str_model_value(data.str_model, "str_gear_torq", "str_gear_torque")
        density = get_material_density(data.material_type)
        modulus = get_material_modulus(data.material_type)
        pinch_roll_teeth = get_str_model_value(data.str_model, "pr_teeth", "pinch_roll_teeth")
        pinch_roll_dp = get_str_model_value(data.str_model, "proll_dp", "pinch_roll_dp")
        str_roll_teeth = get_str_model_value(data.str_model, "sroll_teeth", "str_roll_teeth")
        str_roll_dp = get_str_model_value(data.str_model, "sroll_dp", "str_roll_dp")
        face_width = get_str_model_value(data.str_model, "face_width", "face_width")
        motor_inertia = get_motor_inertia(horsepower_string)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Needed values for calculations
    str_qty = data.num_str_rolls

    # Calculate the coefficient for the constant based on the number of straightener rolls
    if str_qty < 7:
        k_cons = (str_qty / 3.5) + 0.1
    elif str_qty < 9:
        k_cons = str_qty / 3.5
    elif str_qty < 11:
        k_cons = (str_qty / 3.5) - 0.1
    else:
        k_cons = 3

    # Calculate the modulus of elasticity
    if data.str_model == "SPGPS-810" or data.str_model == "CPPS-306" or data.str_model == "CPPS-406" or data.str_model == "CPPS-507":
        ult_tensile_strength = 165100
    else:
        ult_tensile_strength = 128000

    # Calculate Lewis factors for the pinch and straightener rolls
    lewis_factor_pinch = LEWIS_FACTORS[pinch_roll_teeth]
    lewis_factor_str = LEWIS_FACTORS[str_roll_teeth]

    # Calculate the safe working stress
    safe_working_stress = ult_tensile_strength / 3
    accel_time = (data.feed_rate / 60) / data.acceleration

    # Constants
    motor_rpm = MOTOR_RPM
    eff = EFFICIENCY
    pinch_roll_qty = PINCH_ROLL_QTY
    mat_length = MAT_LENGTH
    cont_angle = CONT_ANGLE
    feed_rate_buffer = FEED_RATE_BUFFER

    # Required Force
    required_force = ((16 * data.yield_strength * data.coil_width * (data.material_thickness ** 2) / (15 * center_dist))
                    + (16 * data.yield_strength * data.coil_width * (data.material_thickness ** 2) / (15 * center_dist)) * 0.19)
    
    # Coil Outer Diameter Calculations
    coil_od_measured = sqrt((data.coil_id ** 2) + ((data.max_coil_weight * 4) / (pi * density * data.coil_width)))
    coil_od = min(coil_od_measured, data.coil_od)

    # Pinch / Str Roll / Material length and inertia calculations
    # Pinch Roll
    pinch_roll_length = data.str_width + 2
    pinch_roll_lbs = ((pinch_roll_dia ** 2) / 4) * pi * pinch_roll_length * pinch_roll_qty * 0.283
    pinch_roll_inertia = (pinch_roll_lbs / 32.3) * 0.5 * (((pinch_roll_dia * 0.5) ** 2) / 144) * 12
    pinch_ratio = motor_rpm / ((data.feed_rate * 12) / (pinch_roll_dia * pi))
    pinch_roll_refl_inertia = pinch_roll_inertia / (pinch_ratio ** 2)

    # Straightener Roll
    str_roll_length = data.str_width + 2
    str_roll_lbs = ((str_roll_dia ** 2) / 4) * pi * str_roll_length * data.num_str_rolls * 0.283
    str_roll_inertia = (str_roll_lbs / 32.3) * 0.5 * (((str_roll_dia * 0.5) ** 2) / 144) * 12
    str_ratio = motor_rpm / ((data.feed_rate * 12) / (str_roll_dia * pi))
    str_roll_refl_inertia = str_roll_inertia / (str_ratio ** 2)
    
    # Material Length
    mat_length_lbs = data.material_thickness * data.coil_width * density * mat_length
    mat_length_inertia = (mat_length_lbs / 32.3) * (((pinch_roll_dia * 0.5) ** 2) / 144) * 12
    mat_length_refl_inertia = mat_length_inertia / (pinch_ratio ** 2)

    # Max/Min OD Inertia
    max_od_inertia = (
        (
            (
                (
                    (coil_od ** 2)
                   / 4)
               * pi * data.coil_width * density)
           / 32.3)
       * 0.5 * (
           (
               (coil_od * 0.5)
              ** 2)
          / 144)
       ) * 12
    min_od_inertia = (
        (
            (
                (
                    (data.coil_id ** 2)
                   / 4)
               * pi * data.coil_width * density)
           / 32.3)
       * 0.5 * (
           (
               (data.coil_id * 0.5)
              ** 2)
          / 144)
       ) * 12

    # Max/Min OD Ratios
    max_od_ratio = (coil_od / pinch_roll_dia) * pinch_ratio
    min_od_ratio = (data.coil_id / pinch_roll_dia) * pinch_ratio

    # Max/Min OD Reflective Inertia
    max_od_refl_inertia = max_od_inertia / (max_od_ratio ** 2)
    min_od_refl_inertia = min_od_inertia / (min_od_ratio ** 2)

    # Max/Min OD Total Inertia
    max_od_total_inertia = pinch_roll_refl_inertia + str_roll_refl_inertia + mat_length_refl_inertia + max_od_refl_inertia
    min_od_total_inertia = pinch_roll_refl_inertia + str_roll_refl_inertia + mat_length_refl_inertia + min_od_refl_inertia

    # Torque
    str_torque = (
        (
            (
                (
                    (
                        (
                            (0.667 * data.yield_strength * data.coil_width * (data.material_thickness ** 2)) / center_dist)
                       * 0.35 * data.feed_rate * k_cons)
                   / 33000)
               * 5250)
           / motor_rpm)
       * 12) / eff
    
    # Coil Brake Torque
    coil_brake_torque = (
        (
            (
                (
                    (
                        (coil_od ** 2) / 4)
                   * pi * data.coil_width * density)
               / 32.3 * 0.5 * (
                   (
                       (coil_od * 0.5) ** 2) / 144)
               ) * 12) * (
                   (data.feed_rate * 12) / (coil_od * pi)
                   )
               ) / (9.55 * accel_time)

    # Max/Min OD Brake Torque
    max_od_brake_torque = (coil_brake_torque / ((coil_od / pinch_roll_dia) * pinch_ratio)) / eff
    min_od_brake_torque = (coil_brake_torque / ((data.coil_id / pinch_roll_dia) * pinch_ratio)) / eff

    # Max/Min OD Acceleration Torque
    max_od_accel_torque = (
        (
            (max_od_total_inertia * motor_rpm)
           / (9.55 * accel_time)
           ) * (1 / eff)
           ) + (
               (motor_inertia * motor_rpm)
              / (9.55 * accel_time)
              )
    min_od_accel_torque = (
        (
            (min_od_total_inertia * motor_rpm)
           / (9.55 * accel_time)
           ) * (1 / eff)
           ) + (
               (motor_inertia * motor_rpm)
              / (9.55 * accel_time)
              )

    # Max/Min OD Peak Torque
    max_od_pk_torque = str_torque + max_od_accel_torque + max_od_brake_torque
    min_od_pk_torque = str_torque + min_od_accel_torque + min_od_brake_torque

    # Gear Calculations
    rpm_at_roller_pinch = (data.feed_rate * 12) / (pi * pinch_roll_dia)
    pitch_dia_pinch = pinch_roll_teeth / pinch_roll_dp
    pitch_line_vel_pinch = (pi * rpm_at_roller_pinch * pitch_dia_pinch) / 12
    force_pitchline_pinch = (safe_working_stress * face_width * lewis_factor_pinch * 600) / (pinch_roll_dp * (600 + pitch_line_vel_pinch))
    horsepower_rated_pinch = (force_pitchline_pinch * pitch_line_vel_pinch) / 33000

    rpm_at_roller_str = (data.feed_rate * 12) / (pi * str_roll_dia)
    pitch_dia_str = str_roll_teeth / str_roll_dp
    pitch_line_vel_str = (pi * rpm_at_roller_str * pitch_dia_str) / 12
    force_pitchline_str = (safe_working_stress * face_width * lewis_factor_str * 600) / (str_roll_dp * (600 + pitch_line_vel_str))
    horsepower_rated_str = (force_pitchline_str * pitch_line_vel_str) / 33000

    # Horsepower required
    brake_option = data.auto_brake_compensation.lower()

    if brake_option == "no":
        horsepower_required = (min_od_pk_torque * motor_rpm) / 63000
        accel_torque = min_od_accel_torque
        brake_torque = min_od_brake_torque
    elif brake_option == "yes":
        horsepower_required = (max_od_pk_torque * motor_rpm) / 63000
        accel_torque = max_od_accel_torque
        brake_torque = max_od_brake_torque
    else:
        raise HTTPException(status_code=400, detail="Invalid auto brake compensation value")

    # Pinch Roll
    pinch_roll_req_torque = (str_torque * pinch_ratio / str_gear_torque) + min_od_brake_torque / 2 * pinch_ratio + (((max_od_total_inertia * motor_rpm) / (9.55 * accel_time)) * (1/eff)) * pinch_ratio / 2
    pinch_roll_rated_torque = (63025 * horsepower_rated_pinch) / rpm_at_roller_pinch

    # Str Roll
    str_roll_req_torque = (str_torque * str_ratio / str_gear_torque) + (((max_od_total_inertia * motor_rpm) / (9.55 * accel_time)) * (1 / eff)) * str_ratio / 2 * 7 / 11
    str_roll_rated_torque = (63025 * horsepower_rated_str) / rpm_at_roller_str

    # Actual Coil Weight
    actual_coil_weight = (((coil_od**2) - data.coil_id**2) / 4) * pi * data.coil_width * density

    # Feed Rate check
    feed_rate_check = ""
    if (data.feed_rate >= data.max_feed_rate * feed_rate_buffer and 
        jack_force_available > required_force and
        pinch_roll_rated_torque > pinch_roll_req_torque and
        str_roll_rated_torque > str_roll_req_torque and
        data.horsepower > horsepower_required):
        if get_percent_material_yielded_check(
            roll_str_backbend_state["percent_material_yielded"],
            roll_str_backbend_state["confirm_check"]
        ) == "OK":
            feed_rate_check = "OK"
    else:
        feed_rate_check = "NOT OK"
    
    results = {
        "required_force": round(required_force, 3), 
        "pinch_roll_dia" : round(pinch_roll_dia, 3),
        "pinch_roll_req_torque" : round(pinch_roll_req_torque, 3),
        "pinch_roll_rated_torque" : round(pinch_roll_rated_torque, 3),
        "str_roll_dia": round(str_roll_dia, 3),
        "str_roll_req_torque" : round(str_roll_req_torque, 3),
        "str_roll_rated_torque" : round(str_roll_rated_torque, 3),
        "horsepower_required": round(horsepower_required, 3),

        "center_dist" : round(center_dist, 3),
        "jack_force_available" : round(jack_force_available, 3),
        "max_roll_depth" : round(max_roll_depth, 3),
        "modulus" : round(modulus, 3),
        "pinch_roll_teeth" : round(pinch_roll_teeth, 3),
        "pinch_roll_dp" : round(pinch_roll_dp, 3),
        "str_roll_teeth" : round(str_roll_teeth, 3),
        "str_roll_dp" : round(str_roll_dp, 3),

        "cont_angle" : round(cont_angle, 3),
        "face_width" : round(face_width, 3),
        "actual_coil_weight" : round(actual_coil_weight, 3),
        "coil_od" : round(coil_od, 3),
        "str_torque" : round(str_torque, 3),
        "acceleration_torque" : round(accel_torque, 3),
        "brake_torque" : round(brake_torque, 3),
        "feed_rate_check" : feed_rate_check
    }

    # Save the results to a JSON file
    try:
        append_to_json_list(
            label="str_utility",
            data=results,
            reference_number=rfq_state.reference,
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        return {"error": f"Failed to save results: {str(e)}"}

    return results

@router.post("/{reference}")
def create_str_utility(reference: str, str_utility: StrUtilityCreate = Body(...)):
    """
    Create and persist a new Str Utility entry for a given reference.
    Sets the shared rfq_state to the reference, stores in memory, and appends to JSON file.
    """
    try:
        if not reference or not reference.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")
        # Store in memory
        local_str_utility[reference] = str_utility.dict(exclude_unset=True)
        # Update shared state
        rfq_state.reference = reference
        # Prepare for persistence
        current_str_utility = {reference: str_utility.dict(exclude_unset=True)}
        try:
            append_to_json_list(
                label="str_utility",
                data=current_str_utility,
                reference_number=reference,
                directory=JSON_FILE_PATH
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save Str Utility: {str(e)}")
        return {"message": "Str Utility created", "str_utility": str_utility.dict(exclude_unset=True)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{reference}")
def load_str_utility_by_reference(reference: str):
    """
    Retrieve Str Utility by reference number (memory first, then disk).
    """
    str_utility_from_memory = local_str_utility.get(reference)
    if str_utility_from_memory:
        return {"str_utility": str_utility_from_memory}
    try:
        str_utility_data = load_json_list(
            label="str_utility",
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if str_utility_data:
            return {"str_utility": str_utility_data}
        else:
            return {"error": "Str Utility not found"}
    except FileNotFoundError:
        return {"error": "Str Utility file not found"}
    except Exception as e:
        return {"error": f"Failed to load Str Utility: {str(e)}"}