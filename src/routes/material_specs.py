"""
Material Specifications Calculation Module

"""

from fastapi import APIRouter, Body, HTTPException, Query
from models import MaterialSpecsPayload
import math
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel

# Import the shared lookup table helper function:
from utils.lookup_tables import get_material
from utils.database import get_default_db
from utils.shared import JSON_FILE_PATH, rfq_state

# Initialize FastAPI router
router = APIRouter()

db = get_default_db()

# In-memory storage for material specs
local_material_specs: Dict[str, dict] = {}

class MaterialSpecsCreate(BaseModel):
    # Fields matching the frontend MaterialSpecsCreatePayload interface
    customer: Optional[str] = None
    date: Optional[str] = None
    max_coil_width: Optional[Union[float, str]] = None
    max_coil_weight: Optional[str] = None
    max_material_thickness: Optional[Union[float, str]] = None
    max_material_type: Optional[str] = None
    max_yield_strength: Optional[Union[float, str]] = None
    max_tensile_strength: Optional[Union[float, str]] = None
    full_coil_width: Optional[Union[float, str]] = None
    full_coil_weight: Optional[Union[float, str]] = None
    full_material_thickness: Optional[Union[float, str]] = None
    full_material_type: Optional[str] = None
    full_yield_strength: Optional[Union[float, str]] = None
    full_tensile_strength: Optional[Union[float, str]] = None
    min_coil_width: Optional[Union[float, str]] = None
    min_coil_weight: Optional[Union[float, str]] = None
    min_material_thickness: Optional[Union[float, str]] = None
    min_material_type: Optional[str] = None
    min_yield_strength: Optional[Union[float, str]] = None
    min_tensile_strength: Optional[Union[float, str]] = None
    width_coil_width: Optional[Union[float, str]] = None
    width_coil_weight: Optional[Union[float, str]] = None
    width_material_thickness: Optional[Union[float, str]] = None
    width_material_type: Optional[str] = None
    width_yield_strength: Optional[Union[float, str]] = None
    width_tensile_strength: Optional[Union[float, str]] = None
    coil_id: Optional[str] = None
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
    
    # Additional fields for backward compatibility and calculations
    coil_width_max: Optional[float] = None  # Alias for max_coil_width
    coil_weight_max: Optional[float] = None  # Alias for max_coil_weight
    max_fpm: Optional[float] = None
    max_min_bend_rad: Optional[float] = None
    max_min_loop_length: Optional[float] = None
    max_coil_od: Optional[float] = None
    max_coil_od_calculated: Optional[float] = None
    full_fpm: Optional[float] = None
    full_min_bend_rad: Optional[float] = None
    full_min_loop_length: Optional[float] = None
    full_coil_od: Optional[float] = None
    full_coil_od_calculated: Optional[float] = None
    min_fpm: Optional[float] = None
    min_min_bend_rad: Optional[float] = None
    min_min_loop_length: Optional[float] = None
    min_coil_od: Optional[float] = None
    min_coil_od_calculated: Optional[float] = None
    width_fpm: Optional[float] = None
    width_min_bend_rad: Optional[float] = None
    width_min_loop_length: Optional[float] = None
    width_coil_od: Optional[float] = None
    width_coil_od_calculated: Optional[float] = None

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

@router.post("/calculate")
def calculate_specs(payload: MaterialSpecsCreate) -> Dict[str, Any]:
    """
    Calculate material specifications for all variants using the new flat field names.
    """
    results = {}
    print(payload)
    cWeight = getattr(payload, f"coil_weight_max", None)
    cID = getattr(payload, f"coil_id", None)
    for view in ["max", "full", "min", "width"]:
        mType = getattr(payload, f"{view}_material_type", None)
        thickness = getattr(payload, f"{view}_material_thickness", None)
        yld = getattr(payload, f"{view}_yield_strength", None)
        cWidth = getattr(payload, f"{view}_material_width", None)
        computed = calculate_variant(mType, thickness, yld, cWidth, cWeight, cID)
        results[f"{view}_min_bend_rad"] = computed["min_bend_radius"]
        results[f"{view}_min_loop_length"] = computed["min_loop_length"]
        results[f"{view}_coil_od_calculated"] = computed["coil_od_calculated"]
    # Save to database
    db.create(rfq_state.reference, {**payload.dict(exclude_unset=True), **results})
    return {**payload.dict(exclude_unset=True), **results}

@router.post("/calculate_variant")
def calculate_variant_endpoint(
    payload: VariantCalculationPayload
) -> Dict[str, Any]:
    """
    Calculate material specifications for a single variant using only the required fields.
    Returns the calculated values without any variant prefix.
    """
    computed = calculate_variant(
        payload.material_type,
        payload.material_thickness,
        payload.yield_strength,
        payload.material_width,
        payload.coil_weight_max,
        payload.coil_id
    )
    return {
        "min_bend_rad": computed["min_bend_radius"],
        "min_loop_length": computed["min_loop_length"],
        "coil_od_calculated": computed["coil_od_calculated"]
    }

@router.put("/{reference}")
def update_material_specs(reference: str, specs: MaterialSpecsCreate = Body(...)):
    """
    Update an existing Material Specs entry by reference.
    Only provided fields are updated; all other fields are preserved.
    """
    # Load existing data from database
    record = db.get_by_reference_number(reference)
    if not record:
        raise HTTPException(status_code=404, detail="Material Specs not found")
    record_id = record['id']
    existing = record['data']
    # Merge updates
    updated_specs = dict(existing)
    updated_specs.update(specs.dict(exclude_unset=True))
    local_material_specs[reference] = updated_specs
    # Save to database
    db.update(record_id, updated_specs)
    return {"message": "Material Specs updated", "material_specs": updated_specs}

@router.patch("/{reference}")
def patch_material_specs(reference: str, specs: MaterialSpecsCreate = Body(...)):
    """
    Patch an existing Material Specs entry by reference.
    This endpoint will:
    1. Update existing fields in the JSON with new values
    2. Add new fields that aren't currently in the JSON
    3. Preserve fields not included in the request
    """
    # Load existing data (same approach as PUT method)
    try:
        record = db.get_by_reference_number(reference)
        if not record:
            raise HTTPException(status_code=404, detail="Material Specs not found")
        existing = record['data']
    except Exception:
        raise HTTPException(status_code=404, detail="Material Specs not found")
    
    # Merge updates - only include non-None values
    updated_specs = dict(existing)
    incoming_data = specs.dict()
    
    # Filter out None values - only update fields that have actual values
    non_null_data = {k: v for k, v in incoming_data.items() if v is not None}
    
    print(f"DEBUG: Non-null incoming data: {non_null_data}")
    
    if not non_null_data:
        return {"message": "No non-null data provided to update", "material_specs": existing}
    
    updated_specs.update(non_null_data)
    local_material_specs[reference] = updated_specs
    # Save to database
    record_id = record['id']
    db.update(record_id, updated_specs)
    
    return {"message": f"Material Specs updated with {len(non_null_data)} fields", "material_specs": updated_specs}

@router.post("/{reference}")
def create_material_specs(reference: str, specs: MaterialSpecsCreate = Body(...)):
    """
    Create and persist a new Material Specs entry for a given reference.
    Sets the shared rfq_state to the reference, stores in memory, and appends to JSON file.
    """
    try:
        if not reference or not reference.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")
        local_material_specs[reference] = specs.dict(exclude_unset=True)
        rfq_state.reference = reference
        current_specs = {reference: specs.dict(exclude_unset=True)}
        # Save to database
        db.create(reference, current_specs)
        return {"message": "Material Specs created", "material_specs": specs.dict(exclude_unset=True)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{reference}")
def load_material_specs_by_reference(reference: str):
    specs_from_memory = local_material_specs.get(reference)
    if specs_from_memory:
        data = specs_from_memory
    else:
        # Attempt to retrieve from database
        record = db.get_by_reference_number(reference)
        if record:
            data = record['data']
        else:
            raise HTTPException(status_code=404, detail="No data found for reference")

    # Always ensure all calculated fields are present
    result = {}
    for view in ["max", "full", "min", "width"]:
        # Check if any of the calculated fields for this view are missing
        missing = False
        for suffix in ["_min_bend_rad", "_min_loop_length", "_coil_od_calculated"]:
            key = f"{view}{suffix}"
            if key not in data:
                missing = True
                break
        if missing:
            mType = data.get(f"{view}_material_type")
            thickness = data.get(f"{view}_material_thickness")
            yld = data.get(f"{view}_yield_strength")
            cWidth = data.get(f"{view}_material_width")
            cWeight = data.get("coil_weight_max")
            cID = data.get("coil_id")
            computed = calculate_variant(mType, thickness, yld, cWidth, cWeight, cID)
            result[f"{view}_min_bend_rad"] = computed["min_bend_radius"]
            result[f"{view}_min_loop_length"] = computed["min_loop_length"]
            result[f"{view}_coil_od_calculated"] = computed["coil_od_calculated"]
    merged = dict(data)
    merged.update(result)
    return merged