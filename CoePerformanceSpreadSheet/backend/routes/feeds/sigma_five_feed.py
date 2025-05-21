from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from math import pi, sqrt
import re

# Import your lookup functions
from ..utils.lookup_tables import get_material_density, get_sigma_five_specs, get_selected_str_used
from .physics.inertia import calculate_total_refl_inertia, InertiaInput
from .physics.time import calculate_time, TimeInput
from .physics.regen import calculate_regen, RegenInput

router = APIRouter()

class SigmaFiveInput(BaseModel):
    feed_model: str
    width: int
    loop_pit: str
    full_width_rolls: str
    material_type: str
    application: str
    type_of_line: str

    feed_rate: float
    material_width: int 
    material_thickness: float
    press_bed_length: int
    
    friction_in_die: float
    acceleration_rate: float
    chart_min_length: float
    length_increment: float
    feed_angle_1: float
    feed_angle_2: float

@router.post("/calculate")
def calulate_sigma_five(data: SigmaFiveInput):
    # Lookups
        density = get_material_density(data.material_type)
        max_motor_rpm = get_sigma_five_specs(data.feed_model, "max_mtr_torque", "max_motor_rpm")
        motor_inertia = get_sigma_five_specs(data.feed_model, "mot_inertia", "motor_inertia")
        motor_peak_torque = get_sigma_five_specs(data.feed_model, "mot_peak_torque", "motor_peak_torque")
        motor_rms_torque = get_sigma_five_specs(data.feed_model, "mot_rms_tq", "motor_rms_torque")
        l_roll = get_sigma_five_specs(data.feed_model, "l_roll", "lower_roll")
        u_roll = get_sigma_five_specs(data.feed_model, "u_roll", "upper_roll")
        ratio = get_sigma_five_specs(data.feed_model, "ratio", "ratio")
        efficiency = get_sigma_five_specs(data.feed_model, "efficiency", "efficiency")
        settle_torque = get_sigma_five_specs(data.feed_model, "settle_tor", "settle_torque")
        friction_torque = get_sigma_five_specs(data.feed_model, "fric_torque", "friction_torque")
        watts_lost = get_sigma_five_specs(data.feed_model, "watts_lost", "watts_lost")
        ec = get_sigma_five_specs(data.feed_model, "ec", "ec")
        gb_ratio = get_sigma_five_specs(data.feed_model, "gb_ratio", "gear_box_ratio")
        gb_qty = get_sigma_five_specs(data.feed_model, "gb_qty", "gear_box_qty")
        gb_inertia = get_sigma_five_specs(data.feed_model, "gb_inertia", "gear_box_inertia")
        str_used = get_selected_str_used(data.type_of_line)

        # Max Velocity ft/min
        max_vel = max_motor_rpm / ratio * (l_roll * pi / 720) * 60

        # Frictional Torque
        frictiaonal_torque = (u_roll * 0.5 * data.friction_in_die) / ratio + friction_torque

        # Loop Torque
        if data.loop_pit.lower() == "y" or data.loop_pit.lower() == "yes":
            material_loop = data.material_thickness * 360 * pi * 2
        else:
            material_loop = data.material_thickness * 360 * pi
        loop_torque = ((data.material_width * data.material_thickness * density * material_loop * 0.5) * u_roll * 0.5) / ratio / efficiency

        # Calculate refl inertia
        inertia_input = InertiaInput(
            feed_model = data.feed_model,
            width = data.width,
            thickness = data.material_thickness,
            density = density,
            press_bed_length = data.press_bed_length,
            material_loop = data.material_width,
            ratio = ratio,
            efficiency = efficiency,
            u_roll = u_roll,
            l_roll = l_roll,
            g_box_qty = gb_qty,
            g_box_inertia = gb_inertia, 
            g_box_ratio = gb_ratio, 
        )

        # Calculate refl inertia
        refl_inertia = calculate_total_refl_inertia(inertia_input)

        # Match calculation
        match = refl_inertia / motor_inertia
        if match < 10:
            settle_time = 0.035
        else:
            settle_time = 0.06

        # Velocity and RPM 
        velocity = max_motor_rpm / ratio * (l_roll * pi / 720)
        rpm = ((velocity * 720) / (u_roll * pi)) * ratio

        # Str Max SP
        if str_used.lower() == "y" or str_used.lower() == "yes":
            str_max_sp = data.feed_rate
        else:
            str_max_sp = max_vel

        # Str Max SP Inch
        str_max_sp_inch = str_max_sp * 12

        # Time calculations
        time_import = TimeInput(
            acceleration = data.acceleration_rate,
            application = data.application,
            feed_angle_1 = data.feed_angle_1,
            feed_angle_2 = data.feed_angle_2,
            frictional_torque = frictiaonal_torque,
            increment = data.length_increment,
            loop_torque = loop_torque,
            match = match,

            min_length = data.chart_min_length,
            motor_inertia = motor_inertia,
            motor_rms_torque = motor_rms_torque,
            motor_peak_torque = motor_peak_torque,

            ratio = ratio,
            efficiency = efficiency,
            refl_inertia = refl_inertia,
            rpm = rpm,
            settle_time = settle_time,
            settle_torque = settle_torque,

            str_max_sp = str_max_sp,
            str_max_sp_inch = str_max_sp_inch,
            velocity = velocity,
            width = data.width,
            material_width = data.material_width,
            material_thickness = data.material_thickness,
            press_bed_length = data.press_bed_length,
            density = density,
            material_loop = material_loop
        )

        # Calculate time values
        time_values = calculate_time(time_import)
        feed_angle_1_values = time_values["feed_angle_1"]
        feed_angle_2_values = time_values["feed_angle_2"]

        # Table values
        table_values = []
        if len(feed_angle_1_values) == len(feed_angle_2_values):
            for i in range(len(feed_angle_1_values)):
                table_values.append({
                    "length": feed_angle_1_values[i]["length"],
                    "rms_torque_fa1": feed_angle_1_values[i]["rms_torque"],
                    "rms_torque_fa2": feed_angle_2_values[i]["rms_torque"],
                    "spm_at_fa1": feed_angle_1_values[i]["strokes_per_minute"],
                    "fpm_fa1":  ((feed_angle_1_values[i]["length"] * feed_angle_1_values[i]["strokes_per_minute"]) / 12),
                    "index_time_fa1": feed_angle_1_values[i]["index_time"],
                    "spm_at_fa2": feed_angle_2_values[i]["strokes_per_minute"],
                    "fpm_fa2":  ((feed_angle_2_values[i]["length"] * feed_angle_2_values[i]["strokes_per_minute"]) / 12),
                    "index_time_fa2": feed_angle_2_values[i]["index_time"],
                })

        # Acceleration Torque
        acceleration_torque = (((refl_inertia * rpm) / (9.55 * feed_angle_1_values[0]["acceleration_time"])) / efficiency) + ((motor_inertia * rpm) / (9.55 * feed_angle_1_values[0]["acceleration_time"]))

        # Peak Torque
        peak_torque = acceleration_torque + frictiaonal_torque + loop_torque

        # RMS Torques
        rms_torque_fa1 = sqrt(((peak_torque ** 2 * feed_angle_1_values[0]["acceleration_time"]) + 
                               (acceleration_torque ** 2 * feed_angle_1_values[0]["acceleration_time"]) + 
                               (settle_torque ** 2 * settle_time) + (loop_torque ** 2 * feed_angle_1_values[0]["dwell_time"])) / 
                               (feed_angle_1_values[0]["cycle_time"]))
        rms_torque_fa2 = sqrt(((peak_torque ** 2 * feed_angle_2_values[0]["acceleration_time"]) +
                               (acceleration_torque ** 2 * feed_angle_2_values[0]["acceleration_time"]) + 
                               (settle_torque ** 2 * settle_time) + (loop_torque ** 2 * feed_angle_2_values[0]["dwell_time"])) / 
                               (feed_angle_2_values[0]["cycle_time"]))

        # Calculate Regen
        regen_input = RegenInput(
            match = match,
            motor_inertia = motor_inertia,
            rpm = rpm,
            acceleration_time = feed_angle_1_values[0]["acceleration_time"],
            cycle_time = feed_angle_1_values[0]["cycle_time"],
            watts_lost = watts_lost,
            ec = ec
        )
        regen = calculate_regen(regen_input)

        return {
            "max_motor_rpm": max_motor_rpm,
            "motor_inertia": motor_inertia,
            "max_vel": max_vel,
            "settle_time": settle_time,
            "ratio": ratio,

            "motor_peak_torque": motor_peak_torque,
            "motor_rms_torque": motor_rms_torque,
            "frictiaonal_torque": frictiaonal_torque,
            "loop_torque": loop_torque,
            "settle_torque": settle_torque,

            "regen": regen,

            "refl_inertia": refl_inertia,
            "match": match,
            "peak_torque": peak_torque,
            "rms_torque_fa1": rms_torque_fa1,
            "rms_torque_fa2": rms_torque_fa2,
            "acceleration_torque": acceleration_torque,

            "table_values": table_values,
        }