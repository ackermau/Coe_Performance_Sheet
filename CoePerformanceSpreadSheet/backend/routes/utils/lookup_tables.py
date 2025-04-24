import json
import os

# Build a path to the JSON file relative to this file's location.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_JSON_FILE = os.path.join(_BASE_DIR, "lookup_tables.json")

# Load the JSON file only once at module load time.
with open(_JSON_FILE, "r") as f:
    LOOKUP_DATA = json.load(f)

# Now extract the individual lookup dictionaries
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

def get_material_density(material: str) -> float:
    """Return the density for a given material from the JSON lookup."""
    material_key = material.upper()
    try:
        return lookup_material[material_key]["density"]
    except KeyError:
        raise ValueError(f"Unknown material: {material}")

def get_material_modulus(material: str) -> float:
    """Return the modulus for a given material from the JSON lookup."""
    material_key = material.upper()
    try:
        return lookup_material[material_key]["modulus"]
    except KeyError:
        raise ValueError(f"Unknown material: {material}")


def get_reel_max_weight(reel_model: str) -> int:
    """Return the maximum weight for a given reel model from the JSON lookup."""
    reel_model_key = reel_model.upper()
    try:
        return lookup_reel_dimensions[reel_model_key]["coil_weight"]
    except KeyError:
        raise ValueError(f"Unknown reel model: {reel_model}")

def get_friction(key: str = "DEFAULT") -> float:
    """Return a friction value from the JSON lookup."""
    key = key.upper()
    try:
        return lookup_friction[key]
    except KeyError:
        raise ValueError(f"Unknown friction key: {key}")

def get_fpm_buffer(key: str = "DEFAULT") -> float:
    """Return a FPM buffer value from the JSON lookup."""
    key = key.upper()
    try:
        return lookup_fpm_buffer[key]
    except KeyError:
        raise ValueError(f"Unknown FPM buffer key: {key}")


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


def get_cylinder_bore(brake_model: str) -> float:
    """Return Cylinder Bore Type based off Brake Model"""
    try:
        return lookup_brake_type[brake_model]["cylinder_bore"]
    except KeyError:
        raise ValueError(f"Unknown brake model: {brake_model}")

def get_drive_key(model: str, air_clutch: str, hydThreadingDrive: str) -> str:
    """Return Torque at mandrel based off drive key"""
    try:
        drive_family = lookup_model_families[model]["drive_family"]
        return drive_family + "+" + air_clutch + "+" + hydThreadingDrive
    except KeyError:
        raise ValueError(f"Unknown family: {model}")

def get_drive_torque(drive_key: str) -> float:
    """Return Torque at mandrel based off drive key"""
    try:
        return lookup_drive_torque[drive_key]["torque"]
    except KeyError:
        raise ValueError(f"Unknown drive key: {drive_key}")

def get_press_required(brake_model: str, brake_qty: int, ) -> float:
    """Return Press Required based off Brake Model"""
    try:
        press_required = lookup_press_required[brake_model]["pressure_required"]
    except KeyError:
        raise ValueError(f"Unknown brake model: {brake_model} or {brake_qty}")
    if brake_qty < 1 or brake_qty > 4:
        raise ValueError(f"Brake quantity {brake_qty} out of range (1-4)")
    return press_required / brake_qty

def get_failsafe_holding_force(brake_model: str, brake_qty: int, friction: int, num_brakepads: int, brake_dist: int) -> float:
    """Return Failsafe Holding Force based off Brake Model"""
    try:
        failsafe_holding_force = lookup_press_required[brake_model]["fs_spring_force"]
        holding_force = int(failsafe_holding_force.split(" ")[0])
    except KeyError:
        raise ValueError(f"Unknown brake model: {brake_model} or {brake_qty}")
    if brake_qty < 1 or brake_qty > 4:
        raise ValueError(f"Brake quantity {brake_qty} out of range (1-4)")
    return holding_force * friction * num_brakepads * brake_dist * brake_qty

def get_motor_inertia(motor_hp: str) -> float:
    """Return Motor Inertia based off Motor HP"""
    try:
        return lookup_motor_inertia[motor_hp]["motor_inertia"]
    except KeyError:
        raise ValueError(f"Unknown motor HP: {motor_hp}")

def get_type_of_line(type_of_line: str) -> float:
    """Return Type of Line based off Type of Line"""
    try:
        return lookup_type_of_line[type_of_line]["reel_type"]
    except KeyError:
        raise ValueError(f"Unknown type of line: {type_of_line}")


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

# You can add similar functions for any additional lookup tables if necessary.
