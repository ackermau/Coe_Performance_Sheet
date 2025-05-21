from sys import modules
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field
from math import pi, sqrt
import re

from ..utils.lookup_tables import (
    get_str_model_value,
    get_material_modulus,
);

router = APIRouter()

class RollStrBackbendInput(BaseModel):
    yield_strength: float
    thickness: float
    width: float
    material_type: str
    str_model: str
    num_str_rolls: int

@router.post("/calculate")
def calculate_roll_str_backbend(data: RollStrBackbendInput):
    # Lookups
    try:
        str_roll_dia = get_str_model_value(data.str_model, "roll_diameter", "str_roll_dia")
        center_dist = get_str_model_value(data.str_model, "center_distance", "center_dist")
        jack_force_available = get_str_model_value(data.str_model, "jack_force_avail", "jack_force_available")
        max_roll_depth_without_material = get_str_model_value(data.str_model, "min_roll_depth", "max_roll_depth_without_material")
        top = get_str_model_value(data.str_model, "top", "top")
        bottom = get_str_model_value(data.str_model, "bottom", "bottom")
        modules = get_material_modulus(data.material_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in lookup: {e}")

    if data.num_str_rolls == 7:
        num_mid_rolls = 1
    elif data.num_str_rolls == 9:
        num_mid_rolls = 2
    elif data.num_str_rolls == 11:
        num_mid_rolls = 3
    else:
        raise HTTPException(status_code=400, detail="Invalid roll str backbend value")

    # Values needed for calculations
    creep_factor = .33
    radius_off_coil = -60
    curve_at_yield = 2 * data.yield_strength / (data.thickness * modules)
    radius_at_yield = 1/ curve_at_yield
    bending_moment_to_yield = data.width * data.yield_strength * (data.thickness ** 2) / 6
    if abs(1 / radius_off_coil) > curve_at_yield:
        radius_off_coil_after_springback = 1 / ((1 / radius_off_coil) - ((abs(radius_off_coil) / radius_off_coil) * (1.5 * (1 - creep_factor)) * curve_at_yield * (1 / ((1/3) * (curve_at_yield / (1 / radius_off_coil)) ** 2))))
    else:
        if creep_factor == 0:
            radius_off_coil_after_springback = abs(radius_off_coil) / radius_off_coil * 99999
        else:
            radius_off_coil_after_springback = radius_off_coil / creep_factor

    r_ri = 1 / radius_off_coil_after_springback

    # Max Roller Depth with material
    check = ((str_roll_dia + data.thickness) ** 2) - ((center_dist / 2) ** 2)
    max_roll_depth_with_material = max_roll_depth_without_material
    
    if (str_roll_dia - sqrt(check)) < -str_roll_dia and check >= 0:
        max_roll_depth_with_material = -str_roll_dia + sqrt(check)
    
    # Roller Depth required
    roller_depth_required = -(1.5 * radius_at_yield - data.thickness - 
                              sqrt(abs(((1.5 * radius_at_yield) ** 2) - (center_dist / 2) ** 2)))
    if roller_depth_required > max_roll_depth_without_material:
        roller_depth_required_check = "OK"
    else:
        roller_depth_required_check = "WILL NOT STRAIGHTEN"

    # Roller Table values needed
    main_value = 9843.80654779491

    # Roll Heights (first, mid, last)
    if (main_value - 10000) / 1000 < max_roll_depth_with_material:
        roll_height_first_up = "TOO DEEP!"
    else:
        roll_height_first_up = (main_value - 10000) / 1000

    roll_height_last = data.thickness * 0.8

    # Calculate mid roller heights recursively
    mid_heights = []
    prev_height = roll_height_first_up
    for i in range(num_mid_rolls):
        mid_height = prev_height + (roll_height_last - prev_height) / 2
        mid_heights.append(mid_height)
        prev_height = mid_height

    # Helper function to compute bending results for a roller stage
    def compute_stage_values(res_rad, prev_radius_after_springback):
        r_ri_val = 1 / res_rad - (1 / prev_radius_after_springback)
        if abs(r_ri_val) < curve_at_yield:
            mb_val = (modules * data.width * data.thickness ** 3) / 12 * r_ri_val
        else:
            mb_val = (abs(r_ri_val) / r_ri_val) * 1.5 * bending_moment_to_yield * (1 - (1/3) * ((curve_at_yield / r_ri_val) ** 2))
        mb_my_val = mb_val / bending_moment_to_yield
        springback_val = -curve_at_yield * mb_my_val
        radius_after_springback_val = 1 / ((1 / res_rad) + springback_val)
        return r_ri_val, mb_val, mb_my_val, springback_val, radius_after_springback_val

    # First roller (up and down)
    numerator_first = (-0.25 * center_dist ** 2) - (roll_height_first_up ** 2) + (2 * roll_height_first_up * data.thickness) - data.thickness ** 2
    denominator_first = 4 * (roll_height_first_up + 1e-8) - 4 * data.thickness
    res_rad_first_up = (1.314 - top * data.thickness + bottom * roll_height_first_up) * numerator_first / denominator_first
    res_rad_first_down = -res_rad_first_up

    r_ri_first_up, mb_first_up, mb_my_first_up, springback_first_up, radius_after_springback_first_up = compute_stage_values(res_rad_first_up, radius_off_coil_after_springback)
    r_ri_first_down, mb_first_down, mb_my_first_down, springback_first_down, radius_after_springback_first_down = compute_stage_values(res_rad_first_down, radius_after_springback_first_up)
    r_ri_first_up = 1 / res_rad_first_up - (1 / radius_off_coil_after_springback)

    # Mid rollers
    mid_results = {}
    prev_radius_after_springback_down = radius_after_springback_first_down
    for idx, roll_height_mid in enumerate(mid_heights, start=1):
        numerator_mid = (-0.25 * center_dist ** 2) - (roll_height_mid ** 2) + (2 * roll_height_mid * data.thickness) - data.thickness ** 2
        denominator_mid = 4 * (roll_height_mid + 1e-8) - 4 * data.thickness
        res_rad_mid_up = numerator_mid / denominator_mid
        res_rad_mid_down = -res_rad_mid_up

        r_ri_mid_up, mb_mid_up, mb_my_mid_up, springback_mid_up, radius_after_springback_mid_up = compute_stage_values(res_rad_mid_up, prev_radius_after_springback_down)
        r_ri_mid_down, mb_mid_down, mb_my_mid_down, springback_mid_down, radius_after_springback_mid_down = compute_stage_values(res_rad_mid_down, radius_after_springback_mid_up)

        force_required_mid = mb_mid_up * 5.333 / center_dist

        if abs(r_ri_mid_up) > curve_at_yield:
            percent_yield_mid_up = 1 - abs(curve_at_yield / r_ri_mid_up)
            number_of_yield_strains_mid = 1 / (1 - percent_yield_mid_up)
        else:
            percent_yield_mid_up = "NONE"
            number_of_yield_strains_mid = ""
        if abs(r_ri_mid_down) > curve_at_yield:
            percent_yield_mid_down = 1 - abs(curve_at_yield / r_ri_mid_down)
        else:
            percent_yield_mid_down = "NONE"

        mid_results[f"mid_up_{idx}"] = {
            "roll_height_mid_up": round(roll_height_mid, 3),
            "res_rad_mid_up": round(res_rad_mid_up, 3),
            "r_ri_mid_up": round(r_ri_mid_up, 4),
            "mb_mid_up": round(mb_mid_up, 3),
            "mb_my_mid_up": round(mb_my_mid_up, 4),
            "springback_mid_up": round(springback_mid_up, 4),
            "radius_after_springback_mid_up": round(radius_after_springback_mid_up, 3),
            "force_required_mid_up": round(force_required_mid, 3),
            "percent_yield_mid_up": percent_yield_mid_up,
            "number_of_yield_strains_mid_up": number_of_yield_strains_mid,
        }
        mid_results[f"mid_down_{idx}"] = {
            "res_rad_mid_down": round(res_rad_mid_down, 3),
            "r_ri_mid_down": round(r_ri_mid_down, 4),
            "mb_mid_down": round(mb_mid_down, 3),
            "mb_my_mid_down": round(mb_my_mid_down, 4),
            "springback_mid_down": round(springback_mid_down, 4),
            "radius_after_springback_mid_down": round(radius_after_springback_mid_down, 3),
            "percent_yield_mid_down": percent_yield_mid_down,
        }

        prev_radius_after_springback_down = radius_after_springback_mid_down

    # Last roller
    numerator_last = (-0.25 * center_dist ** 2) - (roll_height_last ** 2) + (2 * roll_height_last * data.thickness) - data.thickness ** 2
    denominator_last = 4 * (roll_height_last + 1e-8) - 4 * data.thickness
    res_rad_last = (1.314 - top * data.thickness + bottom * roll_height_last) * numerator_last / denominator_last

    r_ri_last, mb_last, mb_my_last, springback_last, radius_after_springback_last_val = compute_stage_values(res_rad_last, prev_radius_after_springback_down)
    if abs((1 / res_rad_last) + springback_last) < 1e-5:
        radius_after_springback_last = "FLAT"
    else:
        radius_after_springback_last = radius_after_springback_last_val

    force_required_last = mb_last * 5.333 / center_dist

    if abs(r_ri_first_up) > curve_at_yield:
        percent_yield_first_up = 1 - abs(curve_at_yield / r_ri_first_up)
        number_of_yield_strains_first = 1 / (1 - percent_yield_first_up)
    else:
        percent_yield_first_up = "NONE"
        number_of_yield_strains_first = ""
    if abs(r_ri_first_down) > curve_at_yield:
        percent_yield_first_down = 1 - abs(curve_at_yield / r_ri_first_down)
    else:
        percent_yield_first_down = "NONE"

    if abs(r_ri_last) > curve_at_yield:
        percent_yield_last = 1 - abs(curve_at_yield / r_ri_last)
        number_of_yield_strains_last = 1 / (1 - percent_yield_last)
    else:
        percent_yield_last = "NONE"
        number_of_yield_strains_last = ""

    force_required_first = mb_first_up * 5.333 / center_dist

    result = {
        "roll_diameter": round(str_roll_dia, 4),
        "center_distance": round(center_dist, 4),
        "modules": modules,
        "jack_force_available": jack_force_available,
        "max_roll_depth_without_material": round(max_roll_depth_without_material, 3),
        "max_roll_depth_with_material": round(max_roll_depth_with_material, 3),
        "roller_depth_required": round(roller_depth_required, 3),
        "roller_depth_required_check": roller_depth_required_check,
    }
    result["first_up"] = {
        "roll_height_first_up": round(roll_height_first_up, 3),
        "res_rad_first_up": round(res_rad_first_up, 3),
        "r_ri_first_up": round(r_ri_first_up, 4),
        "mb_first_up": round(mb_first_up, 3),
        "mb_my_first_up": round(mb_my_first_up, 4),
        "springback_first_up": round(springback_first_up, 4),
        "radius_after_springback_first_up": round(radius_after_springback_first_up, 3),
        "force_required_first_up": round(force_required_first, 3),
        "percent_yield_first_up": percent_yield_first_up,
        "number_of_yield_strains_first_up": number_of_yield_strains_first,
    }
    result["first_down"] = {
        "res_rad_first_down": round(res_rad_first_down, 3),
        "r_ri_first_down": round(r_ri_first_down, 4),
        "mb_first_down": round(mb_first_down, 3),
        "mb_my_first_down": round(mb_my_first_down, 4),
        "springback_first_down": round(springback_first_down, 4),
        "radius_after_springback_first_down": round(radius_after_springback_first_down, 3),
        "percent_yield_first_down": percent_yield_first_down,
    }
    for mid_key, mid_data in mid_results.items():
        result[mid_key] = mid_data
    result["last"] = {
        "roll_height_last": round(roll_height_last, 3),
        "res_rad_last": round(res_rad_last, 4),
        "r_ri_last": round(r_ri_last, 3),
        "mb_last": round(mb_last, 3),
        "mb_my_last": round(mb_my_last, 3),
        "springback_last": round(springback_last, 4),
        "radius_after_springback_last": round(radius_after_springback_last, 3) if not isinstance(radius_after_springback_last, str) else radius_after_springback_last,
        "force_required_last": round(force_required_last, 3),
        "percent_yield_last": percent_yield_last,
        "number_of_yield_strains_last": number_of_yield_strains_last,
    }
    return result
  