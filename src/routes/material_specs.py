"""
Material Specifications Calculation Module

"""

from fastapi import APIRouter, Body, HTTPException
from models import MaterialSpecsPayload
import math
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel

# Import the shared lookup table helper function:
from utils.lookup_tables import get_material
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import JSON_FILE_PATH, rfq_state

# Initialize FastAPI router
router = APIRouter()

# In-memory storage for material specs
local_material_specs: Dict[str, dict] = {}

class MaterialSpecsCreate(BaseModel):
    # Only a subset of fields for creation; adjust as needed
    customer: Optional[str] = None
    date: Optional[str] = None
    max_coil_width: Optional[float] = None
    max_coil_weight: Optional[float] = None
    max_material_thickness: Optional[float] = None
    max_material_type: Optional[str] = None
    max_yield_strength: Optional[float] = None
    max_tensile_strength: Optional[float] = None
    max_fpm: Optional[float] = None
    max_min_bend_rad: Optional[float] = None
    max_min_loop_length: Optional[float] = None
    max_coil_od: Optional[float] = None
    max_coil_od_calculated: Optional[float] = None
    full_coil_width: Optional[float] = None
    full_coil_weight: Optional[float] = None
    full_material_thickness: Optional[float] = None
    full_material_type: Optional[str] = None
    full_yield_strength: Optional[float] = None
    full_tensile_strength: Optional[float] = None
    full_fpm: Optional[float] = None
    full_min_bend_rad: Optional[float] = None
    full_min_loop_length: Optional[float] = None
    full_coil_od: Optional[float] = None
    full_coil_od_calculated: Optional[float] = None
    min_coil_width: Optional[float] = None
    min_coil_weight: Optional[float] = None
    min_material_thickness: Optional[float] = None
    min_material_type: Optional[str] = None
    min_yield_strength: Optional[float] = None
    min_tensile_strength: Optional[float] = None
    min_fpm: Optional[float] = None
    min_min_bend_rad: Optional[float] = None
    min_min_loop_length: Optional[float] = None
    min_coil_od: Optional[float] = None
    min_coil_od_calculated: Optional[float] = None
    width_coil_width: Optional[float] = None
    width_coil_weight: Optional[float] = None
    width_material_thickness: Optional[float] = None
    width_material_type: Optional[str] = None
    width_yield_strength: Optional[float] = None
    width_tensile_strength: Optional[float] = None
    width_fpm: Optional[float] = None
    width_min_bend_rad: Optional[float] = None
    width_min_loop_length: Optional[float] = None
    width_coil_od: Optional[float] = None
    width_coil_od_calculated: Optional[float] = None
    feed_direction: Optional[str] = None
    controls_level: Optional[str] = None
    type_of_line: Optional[str] = None
    feed_controls: Optional[str] = None
    passline: Optional[str] = None
    selected_roll: Optional[str] = None
    reel_backplate: Optional[str] = None
    reel_style: Optional[str] = None
    light_guage: Optional[str] = None
    non_marking: Optional[str] = None

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

    # Calculate coil OD based on weight, density, width, and inner diameter
    # Formula: OD = 2 * sqrt((weight/(density * π * width)) + (ID/2)²)
    if coil_width and coil_weight and coil_id and density:
        try:
            # Calculate cross-sectional area term from weight and material properties
            area_term = coil_weight / (density * math.pi * coil_width)
            
            # Calculate inner radius squared term
            radius_term = (coil_id / 2) ** 2
            
            # Calculate outer diameter and round up to nearest integer
            coil_od = math.sqrt(area_term + radius_term) * 2
            coil_od_calculated = math.ceil(coil_od)
            
        except Exception:
            # Return empty string if calculation fails (division by zero, etc.)
            coil_od_calculated = ""
    else:
        # Return empty string if required parameters are missing
        coil_od_calculated = ""
    
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
    for view in ["max", "full", "min", "width"]:
        mType = getattr(payload, f"{view}_material_type", None)
        thickness = getattr(payload, f"{view}_material_thickness", None)
        yld = getattr(payload, f"{view}_yield_strength", None)
        cWidth = getattr(payload, f"{view}_coil_width", None)
        cWeight = getattr(payload, f"{view}_coil_weight", None)
        cID = getattr(payload, f"{view}_coil_id", None)
        computed = calculate_variant(mType, thickness, yld, cWidth, cWeight, cID)
        results[f"{view}_min_bend_rad"] = computed["min_bend_radius"]
        results[f"{view}_min_loop_length"] = computed["min_loop_length"]
        results[f"{view}_coil_od_calculated"] = computed["coil_od_calculated"]
    try:
        append_to_json_list(
            data={rfq_state.reference: {**payload.dict(exclude_unset=True), **results}},
            reference_number=rfq_state.reference,
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        return {"error": f"Failed to save results: {str(e)}"}
    return {**payload.dict(exclude_unset=True), **results}

@router.put("/{reference}")
def update_material_specs(reference: str, specs: MaterialSpecsCreate = Body(...)):
    """
    Update an existing Material Specs entry by reference.
    Only provided fields are updated; all other fields are preserved.
    """
    # Load existing data
    try:
        specs_data = load_json_list(
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if not specs_data or reference not in specs_data:
            raise HTTPException(status_code=404, detail="Material Specs not found")
        existing = specs_data[reference]
    except Exception:
        raise HTTPException(status_code=404, detail="Material Specs not found")
    # Merge updates
    updated_specs = dict(existing)
    updated_specs.update(specs.dict(exclude_unset=True))
    local_material_specs[reference] = updated_specs
    current_specs = {reference: updated_specs}
    try:
        append_to_json_list(
            data=current_specs,
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update Material Specs in storage: {str(e)}"
        )
    return {"message": "Material Specs updated", "material_specs": updated_specs}

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
        try:
            append_to_json_list(
                data=current_specs,
                reference_number=reference,
                directory=JSON_FILE_PATH
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save Material Specs: {str(e)}")
        return {"message": "Material Specs created", "material_specs": specs.dict(exclude_unset=True)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{reference}")
def load_material_specs_by_reference(reference: str):
    specs_from_memory = local_material_specs.get(reference)
    if specs_from_memory:
        return specs_from_memory
    try:
        specs_data = load_json_list(
            reference_number=reference,
            directory=JSON_FILE_PATH
        )
        if specs_data and reference in specs_data:
            data = specs_data[reference]
            # If the data already has calculated fields, return as is
            if any(k.endswith("_min_bend_rad") for k in data.keys()):
                return data
            # Otherwise, treat as base data and calculate
            base_data = data
        else:
            raise HTTPException(status_code=404, detail="No data found for reference")
        result = {}
        for view in ["max", "full", "min", "width"]:
            mType = base_data.get(f"{view}_material_type")
            thickness = base_data.get(f"{view}_material_thickness")
            yld = base_data.get(f"{view}_yield_strength")
            cWidth = base_data.get(f"{view}_coil_width")
            cWeight = base_data.get(f"{view}_coil_weight")
            cID = base_data.get(f"{view}_coil_id")
            computed = calculate_variant(mType, thickness, yld, cWidth, cWeight, cID)
            result[f"{view}_min_bend_rad"] = computed["min_bend_radius"]
            result[f"{view}_min_loop_length"] = computed["min_loop_length"]
            result[f"{view}_coil_od_calculated"] = computed["coil_od_calculated"]
        merged = dict(base_data)
        merged.update(result)
        return merged
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data file not found for reference")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")