from sys import modules
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field
from math import pi, sqrt
import re

from ..utils.lookup_tables import (
    get_material_density,
    get_str_model_value,
);

router = APIRouter()

class RollStrBackbendInput(BaseModel):
    yield_strength: float
    thickness: float
    width: float
    material_type: str
    str_model: str

@router.post("/calculate")
def calculate_seven_roll_str_backbend(data: RollStrBackbendInput):
    # Lookups
    try:
        density = get_material_density()
        str_roll_dia = get_str_model_value(data.str_model, "roll_diameter", "str_roll_dia")
        center_dist = get_str_model_value(data.str_model, "center_distance", "center_dist")
        jack_force_available = get_str_model_value(data.str_model, "jack_force_avail", "jack_force_available")
        max_roll_depth_without_material = get_str_model_value(data.str_model, "min_roll_depth", "max_roll_depth_without_material")
        top = get_str_model_value(data.str_model, "top", "top")
        bottom = get_str_model_value(data.str_model, "bottom", "bottom")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in lookup: {e}")

    # Values needed for calculations
    creep_factor = .33
    radius_off_coil = -60
    r_ri = 1 / radius_off_coil_after_springback
    curve_at_yield = 2 * data.yield_strength / (data.thickness * modules)
    radius_at_yield = 1/ curve_at_yield
    bending_moment_to_yield = data.width * data.yield_strength * (data.thickness ** 2) / 6
    if abs(1 / curve_at_yield) > curve_at_yield:
        radius_off_coil_after_springback = 1 / (
            (1 / radius_off_coil) - (
                (abs(radius_off_coil) / radius_off_coil)
               * (1.5 * (1 - creep_factor)) * curve_at_yield * (1 / (
                   (1/3) * (curve_at_yield / (1 / radius_off_coil)) ** 2))))
    else:
        if creep_factor == 0:
            radius_off_coil_after_springback = abs(radius_off_coil) / radius_off_coil * 99999
        else:
            radius_off_coil_after_springback = radius_off_coil / creep_factor

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
        "WILL NOT STRAIGHTEN"

    # Roller Table values needed
    main_value = 9838

    # Roll Heights (first, mid, last)
    if (main_value - 10000) / 1000 < max_roll_depth_with_material:
        roll_height_first = "TOO DEEP!"
    else:
        roll_height_first = (main_value - 10000) / 1000

    roll_height_last = data.thickness * 0.8
    roll_height_mid = roll_height_first + ((roll_height_last - roll_height_first) / 2)

    # Resulting Radius (first_up, first_down, mid_up, mid_down, last)
    res_rad_first_up = (1.314 - top * data.thickness + bottom * roll_height_first) * (
        (-0.25 * center_dist ** 2) - (roll_height_first ** 2) + 
        (2 * roll_height_first * data.thickness) - data.thickness ** 2) / (4 * (roll_height_first + 0.00000001) - 4 * data.thickness)
    res_rad_first_down = -res_rad_first_up

    res_rad_mid_up = ((-0.25 * center_dist ** 2) - 
                 (roll_height_mid ** 2) + 
                 (2 * roll_height_mid * data.thickness) - 
                 data.thickness ** 2) / (4 * (roll_height_mid + 0.00000001) - 4 * data.thickness)
    res_rad_mid_down = -res_rad_mid_up

    res_rad_last = (1.314 - top * data.thickness + bottom * roll_height_last) * (
        (-0.25 * center_dist ** 2) - (roll_height_last ** 2) + 
        (2 * roll_height_last * data.thickness) - data.thickness ** 2) / (4 * (roll_height_last + 0.00000001) - 4 * data.thickness)

    # First Roller up - 1/r - 1/ri, mb, mb/my, springback, rad_after_springback
    r_ri_first_up = 1 / res_rad_first_up - r_ri
    
    if abs(r_ri_first_up) < curve_at_yield:
        mb_first_up = (modules * data.width * data.thickness ** 3) / (12) * (r_ri_first_up)
    else:
        (abs(r_ri_first_up) / r_ri_first_up) * 1.5 * bending_moment_to_yield * (1 - (1/3) * ((curve_at_yield / r_ri_first_up) ** 2))

    mb_my_first_up = mb_first_up / bending_moment_to_yield
    springback_first_up = -curve_at_yield * mb_my_first_up
    radius_after_springback_first_up = 1 / ((1 / res_rad_first_up) + springback_first_up)

    # First Roller down - 1/r - 1/ri, mb, mb/my, springback, rad_after_springback
    r_ri_first_down = 1 / res_rad_first_down - 1 / radius_after_springback_first_up

    if abs(r_ri_first_down) < curve_at_yield:
        mb_first_down = (modules * data.width * data.thickness ** 3) / (12) * (r_ri_first_down)
    else:
        (abs(r_ri_first_down) / r_ri_first_down) * 1.5 * bending_moment_to_yield * (1 - (1/3) * ((curve_at_yield / r_ri_first_down) ** 2))

    mb_my_first_down = mb_first_down / bending_moment_to_yield
    springback_first_down = -curve_at_yield * mb_my_first_down
    radius_after_springback_first_down = 1 / ((1 / res_rad_first_down) + springback_first_down)

    # Mid Roller up - 1/r - 1/ri, mb, mb/my, springback, rad_after_springback
    r_ri_mid_up = 1 / res_rad_mid_up - 1 / radius_after_springback_first_down

    if abs(r_ri_mid_up) < curve_at_yield:
        mb_mid_up = (modules * data.width * data.thickness ** 3) / (12) * (r_ri_mid_up)
    else:
        (abs(r_ri_mid_up) / r_ri_mid_up) * 1.5 * bending_moment_to_yield * (1 - (1/3) * ((curve_at_yield / r_ri_mid_up) ** 2))
    
    mb_my_mid_up = mb_mid_up / bending_moment_to_yield
    springback_mid_up = -curve_at_yield * mb_my_mid_up
    radius_after_springback_mid_up = 1 / ((1 / res_rad_mid_up) + springback_first_down)

    # Mid Roller down - 1/r - 1/ri, mb, mb/my, springback, rad_after_springback
    r_ri_mid_down = 1 / res_rad_mid_down - 1 / radius_after_springback_mid_up
    
    if abs(r_ri_mid_down) < curve_at_yield:
        mb_mid_down = (modules * data.width * data.thickness ** 3) / (12) * (r_ri_mid_down)
    else:
        (abs(r_ri_mid_down) / r_ri_mid_down) * 1.5 * bending_moment_to_yield * (1 - (1/3) * ((curve_at_yield / r_ri_mid_down) ** 2))

    mb_my_mid_down = mb_mid_down / bending_moment_to_yield
    springback_mid_down = -curve_at_yield * mb_my_mid_down
    radius_after_springback_mid_down = 1 / ((1 / res_rad_mid_down) + springback_mid_down)

    # Last Roller - 1/r - 1/ri, mb, mb/my, springback, rad_after_springback
    r_ri_last = 1 / res_rad_last - 1 / radius_after_springback_mid_down

    if abs(r_ri_last) < curve_at_yield:
        mb_last = (modules * data.width * data.thickness ** 3) / (12) * (r_ri_last)
    else:
        (abs(r_ri_last) / r_ri_last) * 1.5 * bending_moment_to_yield * (1 - (1/3) * ((curve_at_yield / r_ri_last) ** 2))

    mb_my_last = mb_last / bending_moment_to_yield
    springback_last = -curve_at_yield * mb_my_last

    if abs((1 / res_rad_last) + springback_last) < 0.00001:
        radius_after_springback_last = "FLAT"
    else:
        radius_after_springback_last = 1 / ((1 / res_rad_last) + springback_last)

    # Force Required (first, mid, last)
    force_required_first = mb_first_up * 5.333 / center_dist
    force_required_mid = mb_mid_up * 5.333 / center_dist
    force_required_last = mb_last * 5.333 / center_dist

    # Percent of material thickness yielded and Number of yield strains at surface (first_up, first_down, mid_up, mid_down, last)
    if curve_at_yield < abs(r_ri_first_up):
        percent_yield_first_up = 1 - abs(curve_at_yield / r_ri_first_up)
        number_of_yield_strains_first = 1 / (1 - percent_yield_first_up)
    else:
        percent_yield_first_up = "NONE"
        number_of_yield_strains_first = ""

    if curve_at_yield < abs(r_ri_first_down):
        percent_yield_first_down = 1 - abs(curve_at_yield / r_ri_first_down)
    else:
        percent_yield_first_down = "NONE"

    if curve_at_yield < abs(r_ri_mid_up):
        percent_yield_mid_up = 1 - abs(curve_at_yield / r_ri_mid_up)
        number_of_yield_strains_mid = 1 / (1 - percent_yield_mid_up)
    else:
        percent_yield_mid_up = "NONE"
        number_of_yield_strains_mid = ""

    if curve_at_yield < abs(r_ri_mid_down):
        percent_yield_mid_down = 1 - abs(curve_at_yield / r_ri_mid_down)
    else:
        percent_yield_mid_down = "NONE"

    if curve_at_yield < abs(r_ri_last):
        percent_yield_last = 1 - abs(curve_at_yield / r_ri_last)
        number_of_yield_strains_last = 1 / (1 - percent_yield_last)
    else:
        percent_yield_last = "NONE"
        number_of_yield_strains_last = ""

    return {
        "roll_diameter": round(str_roll_dia, 3),
        "center_distance": center_dist,
        "jack_force_available": jack_force_available,
        "max_roll_depth_without_material": round(max_roll_depth_without_material, 3),
        "max_roll_depth_with_material": round(max_roll_depth_with_material, 3),
        "roller_depth_required": round(roller_depth_required, 3),

        "first": {
            "up": {
                "roll_height_first": round(roll_height_first, 3),
                "res_rad_first_up": round(res_rad_first_up, 3),
                "r_ri_first_up": round(r_ri_first_up, 3),
                "mb_first_up": round(mb_first_up, 3),
                "mb_my_first_up": round(mb_my_first_up, 3),
                "springback_first_up": round(springback_first_up, 3),
                "radius_after_springback_first_up": round(radius_after_springback_first_up, 3),
                "force_required_first": round(force_required_first, 3),
                "percent_yield_first_up": percent_yield_first_up,
                "number_of_yield_strains_first": number_of_yield_strains_first,
            },
            "down": {
                "res_rad_first_down": round(res_rad_first_down, 3),
                "r_ri_first_down": round(r_ri_first_down, 3),
                "mb_first_down": round(mb_first_down, 3),
                "mb_my_first_down": round(mb_my_first_down, 3),
                "springback_first_down": round(springback_first_down, 3),
                "radius_after_springback_first_down": round(radius_after_springback_first_down, 3),
                "percent_yield_first_down": percent_yield_first_down,
            }
        },
        "mid": {
            "up": {
                "roll_height_mid": round(roll_height_mid, 3),
                "res_rad_mid_up": round(res_rad_mid_up, 3),
                "r_ri_mid_up": round(r_ri_mid_up, 3),
                "mb_mid_up": round(mb_mid_up, 3),
                "mb_my_mid_up": round(mb_my_mid_up, 3),
                "springback_mid_up": round(springback_mid_up, 3),
                "radius_after_springback_mid_up": round(radius_after_springback_mid_up, 3),
                "force_required_mid": round(force_required_mid, 3),
                "percent_yield_mid_up": percent_yield_mid_up,
                "number_of_yield_strains_mid": number_of_yield_strains_mid,
            },
            "down": {
                "res_rad_mid_down": round(res_rad_mid_down, 3),
                "r_ri_mid_down": round(r_ri_mid_down, 3),
                "mb_mid_down": round(mb_mid_down, 3),
                "mb_my_mid_down": round(mb_my_mid_down, 3),
                "springback_mid_down": round(springback_mid_down, 3),
                "radius_after_springback_mid_down": round(radius_after_springback_mid_down, 3),
                "percent_yield_mid_down": percent_yield_mid_down,
            }
        },
        "last": {
            "roll_height_last": round(roll_height_last, 3),
            "res_rad_last": round(res_rad_last, 3),
            "r_ri_last": round(r_ri_last, 3),
            "mb_last": round(mb_last, 3),
            "mb_my_last": round(mb_my_last, 3),
            "springback_last": round(springback_last, 3),
            "radius_after_springback_last": round(radius_after_springback_last, 3),
            "force_required_last": round(force_required_last, 3),
            "percent_yield_last": percent_yield_last,
            "number_of_yield_strains_last": number_of_yield_strains_last,
        }
    }