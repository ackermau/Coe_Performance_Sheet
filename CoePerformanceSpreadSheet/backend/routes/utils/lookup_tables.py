import json
import os

# Build a path to the JSON file relative to this file's location.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_JSON_FILE = os.path.join(_BASE_DIR, "lookup_tables.json")

# Load the JSON file only once at module load time.
with open(_JSON_FILE, "r") as f:
    LOOKUP_DATA = json.load(f)

# Now extract the individual lookup dictionaries
#####
# TDDBHD
#####
lookup_material = LOOKUP_DATA.get("lookup_material", {})
lookup_reel_dimensions = LOOKUP_DATA.get("lookup_reel_dimensions", {})
lookup_friction = LOOKUP_DATA.get("lookup_friction", {})
lookup_fpm_buffer = LOOKUP_DATA.get("lookup_fpm_buffer", {})
lookup_model_families = LOOKUP_DATA.get("lookup_model_families", {})
lookup_holddown_sort = LOOKUP_DATA.get("lookup_holddown_sort", {})
lookup_brake_type = LOOKUP_DATA.get("lookup_brake_type", {})
lookup_holddown_matrix = LOOKUP_DATA.get("lookup_holddown_matrix", {})
lookup_drive_torque = LOOKUP_DATA.get("lookup_drive_key", {})
lookup_press_required = LOOKUP_DATA.get("lookup_press_required", {})
lookup_motor_inertia = LOOKUP_DATA.get("lookup_motor_inertia", {})
lookup_type_of_line = LOOKUP_DATA.get("lookup_type_of_line", {})
#####
# STR Utility
#####
lookup_str_model = LOOKUP_DATA.get("lookup_str_model", {})

######
# TDDBHD methods
######
## Material Density
def get_material_density(material: str) -> float:
    """Return the density for a given material from the JSON lookup."""
    material_key = material.upper()
    try:
        return lookup_material[material_key]["density"]
    except KeyError:
        raise ValueError(f"Unknown material: {material}")

## Material Modulus
def get_material_modulus(material: str) -> float:
    """Return the modulus for a given material from the JSON lookup."""
    material_key = material.upper()
    try:
        return lookup_material[material_key]["modulus"]
    except KeyError:
        raise ValueError(f"Unknown material: {material}")

## Reel Max Weight
def get_reel_max_weight(reel_model: str) -> int:
    """Return the maximum weight for a given reel model from the JSON lookup."""
    reel_model_key = reel_model.upper()
    try:
        return lookup_reel_dimensions[reel_model_key]["coil_weight"]
    except KeyError:
        raise ValueError(f"Unknown reel model: {reel_model}")

## FPM Buffer
def get_fpm_buffer(key: str = "DEFAULT") -> float:
    """Return a FPM buffer value from the JSON lookup."""
    key = key.upper()
    try:
        return lookup_fpm_buffer[key]
    except KeyError:
        raise ValueError(f"Unknown FPM buffer key: {key}")

## Holddown Matrix
def get_hold_down_matrix_label(model: str, hold_down_assy: str, cylinder: str) -> str:
    """Form and return hold down matrix label."""
    try:
        hold_down_family = lookup_model_families[model]["holddown_family"]
    except KeyError:
        raise ValueError(f"Unknown family: {model}")

    try:
        holddown_sort = lookup_holddown_sort[hold_down_assy]["sort"]
    except KeyError:
        raise ValueError(f"Unknown holddown assembly: {hold_down_assy}")

    return f"{hold_down_family}+{holddown_sort}+{hold_down_assy}+{cylinder}"

## Pressure PSI
def get_pressure_psi(holddown_matrix_key: str, air_pressure: float) -> float:
    """Return pressure psi based off Holddown Matrix Key"""
    holddown_matrix = next(
    (entry for entry in lookup_holddown_matrix if entry["key"] == holddown_matrix_key),
    None  # default if not found
    )
    if holddown_matrix is None:
        raise ValueError(f"Holddown matrix key {holddown_matrix_key} not found")

    pressure_label = holddown_matrix["PressureLabel"]
    max_psi = holddown_matrix["MaxPSI"]
    psi = holddown_matrix["PSI"]

    if "psi Air" in pressure_label:
        return min(air_pressure, max_psi)
    else:
        return psi

## Holddown Force Available
def get_holddown_force_available(holddown_matrix_key: str, holddown_pressure: str) -> float:
    """Return Force Factor based off Holddown Matrix Key"""
    holddown_matrix = next(
        (entry for entry in lookup_holddown_matrix if entry["key"] == holddown_matrix_key),
        None  # default if not found
    )
    if holddown_matrix is None:
        raise ValueError(f"Holddown matrix key {holddown_matrix_key} not found")

    force_factor = holddown_matrix["ForceFactor"]
    return force_factor * holddown_pressure

## Min Material Width
def get_min_material_width(holddown_matrix_key: str) -> float:
    """Return Min Material Width based off Holddown Matrix Key"""
    holddown_matrix = next(
        (entry for entry in lookup_holddown_matrix if entry["key"] == holddown_matrix_key),
        None  # default if not found
    )
    if holddown_matrix is None:
        raise ValueError(f"Holddown matrix key {holddown_matrix_key} not found")

    min_material_width = holddown_matrix["MinWidth"]
    return min_material_width

## Cylinder bore
def get_cylinder_bore(brake_model: str) -> float:
    """Return Cylinder Bore Type based off Brake Model"""
    try:
        return lookup_brake_type[brake_model]["cylinder_bore"]
    except KeyError:
        raise ValueError(f"Unknown brake model: {brake_model}")

## Drive Key
def get_drive_key(model: str, air_clutch: str, hydThreadingDrive: str) -> str:
    """Return Torque at mandrel based off drive key"""
    try:
        drive_family = lookup_model_families[model]["drive_family"]
        return drive_family + "+" + air_clutch + "+" + hydThreadingDrive
    except KeyError:
        raise ValueError(f"Unknown family: {model}")

## Drive Torque
def get_drive_torque(drive_key: str) -> float:
    """Return Torque at mandrel based off drive key"""
    try:
        return lookup_drive_torque[drive_key]["torque"]
    except KeyError:
        raise ValueError(f"Unknown drive key: {drive_key}")

## Motor Inertia
def get_motor_inertia(motor_hp: str) -> float:
    """Return Motor Inertia based off Motor HP"""
    try:
        return lookup_motor_inertia[motor_hp]["motor_inertia"]
    except KeyError:
        raise ValueError(f"Unknown motor HP: {motor_hp}")

## Type of Line
def get_type_of_line(type_of_line: str) -> float:
    """Return Type of Line based off Type of Line"""
    try:
        return lookup_type_of_line[type_of_line]["reel_type"]
    except KeyError:
        raise ValueError(f"Unknown type of line: {type_of_line}")

## Reel Dimensions
def get_reel_dimensions(model: str) -> dict:
    """
    Return all data for a given reel model from the JSON lookup.

    Example:
        {
          "size": 20,
          "bearing_dist": 12,
          "fbearing_dist": 10,
          "rbearing_dist": 8
          "coil_weight": 1000,
          "mandrel_dia": 5,
          "backplate": 15,
          "full_od_backplate": 20,
          "backplate_thickness": 2
    }
    """
    reel_key = model.upper()
    try:
        return lookup_reel_dimensions[reel_key]
    except KeyError:
        raise ValueError(f"Unknown reel model: {model}")

## Material
def get_material(material: str) -> dict:
    """
    Return all data for a given material from the JSON lookup.

    Example:
        {
          "yield": 20000,
          "modulus": 10600000,
          "density": 0.0980
        }
    """
    material_key = material.upper()
    try:
        return lookup_material[material_key]
    except KeyError:
        raise ValueError(f"Unknown material: {material}")

#####
# STR Utility methods
#####
## Center Distance
def get_center_dist(model: str) -> float:
    """Return Center Dist for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["center_distance"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")

## Str Roll Dia
def get_str_roll_dia(model: str) -> float:
    """Return Str Roll Dia for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["roll_diameter"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")

## Pinch Roll Dia
def get_pinch_roll_dia(model: str) -> float:
    """Return Pinch Roll Dia for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["pinch_roll_dia"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")

## Jack Force Available
def get_jack_force_available(model: str) -> float:
    """Return Jack Force Available for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["jack_force_avail"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")

## Max Roll Depth
def get_max_roll_depth(model: str) -> float:
    """Return Max Roll Depth for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["min_roll_depth"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")

## Str Gear Torque
def get_str_gear_torque(model: str) -> float:
    """Return Str Gear Torque for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["str_gear_torq"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")

## Pinch Roll Teeth
def get_pinch_roll_teeth(model: str) -> int:
    """Return Pinch Roll Teeth for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["pr_teeth"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")
    
## Pinch Roll DP
def get_pinch_roll_dp(model: str) -> float:
    """Return Pinch Roll DP for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["proll_dp"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")

## Str Roll Teeth
def get_str_roll_teeth(model: str) -> int:
    """Return Str Roll Teeth for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["sroll_teeth"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")

## Str Roll DP
def get_str_roll_dp(model: str) -> float:
    """Return Str Roll DP for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["sroll_dp"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")

## Face Width
def get_face_width(model: str) -> float:
    """Return Face Width for a given model from the JSON lookup."""
    model_key = model.upper()
    try:
        return lookup_str_model[model_key]["face_width"]
    except KeyError:
        raise ValueError(f"Unknown model: {model}")
