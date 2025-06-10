from pydantic import BaseModel
from typing import Optional

######################################################
# Base Calculation Models
######################################################
# RFQ is used to define the structure of a Request for Quotation
class RFQ(BaseModel):
    # Basic details
    id: int
    date: str # Date in YYYY-MM-DD format
    reference: str

    company_name: str
    state_province: str
    street_address: str
    zip_code: int
    city: str
    country: str

    contact_name: str
    contact_position: str
    contact_phone_number: str 
    contact_email: str

    days_per_week_running: int
    shifts_per_day: int

    line_application: str
    type_of_line: str
    pull_thru: str

    # Coil specifications
    max_coil_width: float
    min_coil_width: float
    max_coil_od: float
    coil_id: float
    max_coil_weight: float
    max_coil_handling_cap: float

    type_of_coil: str
    coil_car: bool
    run_off_backplate: bool
    req_rewinding: bool

    # Material specifications
    # max
    max_material_thickness: float
    max_material_width: float
    max_material_type: str
    max_yield_strength: float
    max_tensile_strength: float

    # full
    full_material_thickness: float
    full_material_width: float
    full_material_type: str
    full_yield_strength: float
    full_tensile_strength: float

    # min
    min_material_thickness: float
    min_material_width: float
    min_material_type: str
    min_yield_strength: float
    min_tensile_strength: float

    # width
    width_material_thickness: float
    width_material_width: float
    width_material_type: str
    width_yield_strength: float
    width_tensile_strength: float

    cosmetic_material: bool
    brand_of_feed_equipment: str
    
    # Type of press
    gap_frame_press: bool
    hydraulic_press: bool
    obi: bool
    servo_press: bool
    shear_die_application: bool
    straight_side_press: bool
    other: bool

    tonnage_of_press: str


# MaterialSpecsPayload is used to define the payload structure for material specifications
class MaterialSpecsPayload(BaseModel):
    # Max view
    material_type_max: str = None
    material_thickness_max: float = None  # in inches
    yield_strength_max: float = None       # in psi
    coil_width_max: float = None           # in inches
    coil_weight_max: float = None          # in lbs
    coil_id_max: float = None              # in inches

    # Full view
    material_type_full: str = None
    material_thickness_full: float = None
    yield_strength_full: float = None
    coil_width_full: float = None
    coil_weight_full: float = None
    coil_id_full: float = None

    # Min view
    material_type_min: str = None
    material_thickness_min: float = None
    yield_strength_min: float = None
    coil_width_min: float = None
    coil_weight_min: float = None
    coil_id_min: float = None

    # Width view
    material_type_width: str = None
    material_thickness_width: float = None
    yield_strength_width: float = None
    coil_width_width: float = None
    coil_weight_width: float = None
    coil_id_width: float = None

# TDDBHDInput is used to define the input structure for TDDBHD calculations
class TDDBHDInput(BaseModel):
    type_of_line: str
    reel_drive_tqempty: Optional[float]
    motor_hp: Optional[float]

    yield_strength: float
    thickness: float
    width: float
    coil_id: float
    coil_od: float
    coil_weight: float

    decel: float
    friction: float
    air_pressure: float

    brake_qty: int
    brake_model: str

    cylinder: str
    hold_down_assy: str
    hyd_threading_drive: str
    air_clutch: str
    
    # For lookup: note the field name expected is material_type (with a capital T)
    material_type: str
    reel_model: str

# ReelDriveInput is used to define the input structure for reel drive calculations    
class ReelDriveInput(BaseModel):
    model: str
    material_type: str
    coil_id: float
    coil_od: float
    reel_width: float
    backplate_diameter: float
    motor_hp: float
    type_of_line: str
    required_max_fpm: Optional[float] = 0

# StrUtilityInput is used to define the input structure for strapping utility calculations
class StrUtilityInput(BaseModel):
    max_coil_weight: float
    coil_id: float
    coil_od: float
    coil_width: float
    material_thickness: float
    yield_strength: float
    material_type: str

    str_model: str
    str_width: float
    horsepower: float

    feed_rate: float
    max_feed_rate: float
    auto_brake_compensation: str
    acceleration: float
    num_str_rolls: int

##################################################
# Rolls Calculation Models
##################################################
# RollStrBackbendInput is used to define the input structure for roll str backbend calculations
class RollStrBackbendInput(BaseModel):
    yield_strength: float
    thickness: float
    width: float
    material_type: str
    str_model: str
    num_str_rolls: int
    calc_const: Optional[float]

##################################################
# Physics Calculation Models
##################################################
# InertiaInput is used to define the input structure for inertia calculations
class InertiaInput(BaseModel):
    feed_model: str
    width: int
    thickness: float
    density: float
    press_bed_length: int
    material_loop: float
    ratio: float
    efficiency: float
    roll_width: str
    material_width: int

# RegenInput is used to define the input structure for regenerative braking calculations
class RegenInput(BaseModel):
    match: float
    motor_inertia: float
    rpm: float
    acceleration_time: float
    cycle_time: float
    watts_lost: float
    ec: float

# TimeInput is used to define the input structure for time calculations
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

##################################################
# Feed Calculation Models
##################################################
# BaseFeedParams is used to define the common parameters for feed calculations
class BaseFeedParams(BaseModel):
    feed_model: str
    width: int
    loop_pit: str

    material_type: str
    application: str
    type_of_line: str
    roll_width: str
    feed_rate: Optional[float]
    material_width: int 
    material_thickness: float
    press_bed_length: int

    friction_in_die: float
    acceleration_rate: float
    chart_min_length: float
    length_increment: float
    feed_angle_1: float
    feed_angle_2: float

# FeedInput is used to define the input structure for feed calculations
class FeedInput(BaseFeedParams):
    pass

# AllenBradleyInput is used to define the input structure for Allen-Bradley feed calculations
class AllenBradleyInput(BaseFeedParams):
    pass

# FeedWPullThruInput is used to define the input structure for feed with pull-thru calculations
class FeedWPullThruInput(BaseFeedParams):
    straightening_rolls: int
    yield_strength: float
    str_pinch_rolls: str
    req_max_fpm: float

######################################################
# Shear Calculation Models
######################################################
class HydShearInput(BaseModel):
    max_material_thickness: float
    coil_width: float
    material_tensile: float

    rake_of_blade: float
    overlap: float
    blade_opening: float
    percent_of_penetration: float

    bore_size: float
    rod_dia: float
    stroke: float

    pressure: float

    time_for_down_stroke: float
    dwell_time: float


######################################################
# ZigZag Calculation Models
######################################################
# ZigZagInput is used to define the input structure for zigzag calculations
class ZigZagInput(BaseModel):
    material_width: float
    material_thickness: float
    material_length_flat: float
    material_density: float

    pivot_to_screw: float
    total_load: float
    efficiency: float
    feed_angle: float
    misc_friction_at_motor: float

    lead_screw_o_dia: float
    lead_screw_i_dia: float
    lead_screw_length: float
    lead_screw_density: float
    lead_screw_qty: int

    min_length: float
    incriment: float