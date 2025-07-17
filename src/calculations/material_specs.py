"""
Material Specifications Calculation Module

"""
from models import MaterialSpecsPayload
import math
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel

# Import the shared lookup table helper function:
from utils.lookup_tables import get_material
from utils.database import get_default_db
from utils.shared import JSON_FILE_PATH, rfq_state

db = get_default_db()

# In-memory storage for material specs
local_material_specs: Dict[str, dict] = {}

class MaterialSpecsCreate(BaseModel):
    # Fields for a single material spec variant
    customer: Optional[str] = None
    date: Optional[str] = None
    coil_width: Optional[Union[float, str]] = None
    coil_weight: Optional[Union[float, str]] = None
    material_thickness: Optional[Union[float, str]] = None
    material_type: Optional[str] = None
    yield_strength: Optional[Union[float, str]] = None
    tensile_strength: Optional[Union[float, str]] = None
    coil_id: Optional[Union[float, str]] = None
    feed_direction: Optional[str] = None
    controls_level: Optional[str] = None
    type_of_line: Optional[str] = None
    feed_controls: Optional[str] = None
    passline: Optional[str] = None
    selected_roll: Optional[str] = None
    reel_backplate: Optional[str] = None
    reel_style: Optional[str] = None
    light_guage: Optional[bool] = None
    non_marking: Optional[bool] = None
    # Additional calculated fields
    min_bend_radius: Optional[float] = None
    min_loop_length: Optional[float] = None
    coil_od_calculated: Optional[float] = None

class VariantCalculationPayload(BaseModel):
    material_type: str
    material_thickness: float
    yield_strength: float
    material_width: float
    coil_weight_max: float
    coil_id: float

def to_float(val):
    try:
        if isinstance(val, str) and val.strip() != "":
            return float(val)
        elif isinstance(val, (int, float)):
            return float(val)
    except Exception as e:
        print(f"Could not convert value to float: {val} ({e})")
    return None

def calculate_variant(
    materialType: Optional[str], 
    thickness: Optional[float], 
    yield_strength: Optional[float], 
    coil_width: Optional[float], 
    coil_weight: Optional[float], 
    coil_id: Optional[float]
) -> Dict[str, Union[float, int, str]]:
    """
    Calculate material specifications for a single variant.
    
    Performs calculations for minimum bend radius, minimum loop length,
    and calculated coil outer diameter based on material properties
    and dimensional parameters.
    
    Args:
        materialType (Optional[str]): Material type identifier for lookup
        thickness (Optional[float]): Material thickness in inches
        yield_strength (Optional[float]): Material yield strength in PSI
        coil_width (Optional[float]): Coil width in inches
        coil_weight (Optional[float]): Coil weight in pounds
        coil_id (Optional[float]): Coil inner diameter in inches
        
    Returns:
        Dict[str, Union[float, int, str]]: Dictionary containing:
            - min_bend_radius: Minimum bend radius in inches (float)
            - min_loop_length: Minimum loop length in feet (float)  
            - coil_od_calculated: Calculated coil outer diameter (int or empty string)
            
    """
    
    # Look up material properties using shared lookup table
    try:
        mat = get_material(materialType)
    except ValueError:
        # Default to empty dict if material type not found
        mat = {}
        
    # Extract material properties from lookup result
    modulus = mat.get("modulus")      # Material modulus of elasticity
    density = mat.get("density")      # Material density
    
    # Formula: min_bend_radius = (modulus * (thickness/2)) / yield_strength
    if thickness and yield_strength and modulus:
        min_bend_radius = round((modulus * (thickness / 2)) / yield_strength, 4)
    else:
        min_bend_radius = 0

    # Formula: min_loop_length = (min_bend_radius * 4) / 12
    # Factor of 4 accounts for loop geometry, division by 12 converts inches to feet
    if min_bend_radius > 0:
        min_loop_length = round((min_bend_radius * 4) / 12, 4)
    else:
        min_loop_length = 0

    coil_weight = to_float(coil_weight)
    density = to_float(density)
    coil_width = to_float(coil_width)
    coil_id = to_float(coil_id)

    # Calculate coil OD based on weight, density, width, and inner diameter
    # Formula: OD = 2 * sqrt((weight/(density * π * width)) + (ID/2)²)
    valid_types = (int, float)
    if all(isinstance(x, valid_types) and x is not None for x in [coil_weight, density, coil_width, coil_id]):
        try:
            # Calculate cross-sectional area term from weight and material properties
            area_term = coil_weight / (density * math.pi * coil_width)
            # Calculate inner radius squared term
            radius_term = (coil_id / 2) ** 2
            # Calculate outer diameter and round up to nearest integer
            if area_term + radius_term >= 0:
                coil_od = math.sqrt(area_term + radius_term) * 2
                coil_od_calculated = math.ceil(coil_od)
            else:
                coil_od_calculated = 0
        except Exception as e:
            coil_od_calculated = 0
    else:
        coil_od_calculated = 0
    
    return {
        "min_bend_radius": min_bend_radius,
        "min_loop_length": min_loop_length,
        "coil_od_calculated": coil_od_calculated
    }

def calculate_specs(payload: MaterialSpecsCreate) -> Dict[str, Any]:
    """
    Calculate material specifications for a single variant.
    """
    computed = calculate_variant(
        payload.material_type,
        payload.material_thickness,
        payload.yield_strength,
        payload.coil_width,
        payload.coil_weight,
        payload.coil_id
    )
    # Save to database
    db.create(rfq_state.reference, {**payload.dict(exclude_unset=True), **computed})
    return {**payload.dict(exclude_unset=True), **computed}
