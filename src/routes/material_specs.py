"""
Material Specifications Calculation Module

"""

from fastapi import APIRouter
from models import MaterialSpecsPayload
import math
from typing import Dict, Any, Optional, Union

# Import the shared lookup table helper function:
from utils.lookup_tables import get_material
from utils.json_util import load_json_list, append_to_json_list
from utils.shared import JSON_FILE_PATH, rfq_state

# Initialize FastAPI router
router = APIRouter()

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
def calculate_specs(payload: MaterialSpecsPayload) -> Dict[str, Any]:
    """
    Calculate material specifications for all variants.
    
    Processes material specifications for four different variants (max, full, min, width)
    by extracting parameters for each variant and performing calculations.
    Results are saved to JSON storage and returned.
    
    Args: \n
        payload (MaterialSpecsPayload): Input payload containing material parameters
            for all variants. Each variant should have:
            - material_type_{variant}: Material type identifier
            - material_thickness_{variant}: Material thickness in inches
            - yield_strength_{variant}: Material yield strength in PSI
            - coil_width_{variant}: Coil width in inches
            - coil_weight_{variant}: Coil weight in pounds
            - coil_id_{variant}: Coil inner diameter in inches
            
    Returns: \n
        Dict[str, Any]: Results dictionary containing calculated values for all variants:
            - min_bend_radius_{variant}: Minimum bend radius for each variant
            - min_loop_length_{variant}: Minimum loop length for each variant
            - coil_od_calculated_{variant}: Calculated coil OD for each variant
            
    Error Handling: \n
        Returns error dictionary if JSON save operation fails
        
    """
    
    # Initialize results dictionary
    results = {}
    
    # Process each variant individually
    # Variants: max, full, min, width
    for view in ["max", "full", "min", "width"]:
        
        # Extract parameters for current variant using getattr with fallback to None
        mType = getattr(payload, f"material_type_{view}", None)
        thickness = getattr(payload, f"material_thickness_{view}", None)
        yld = getattr(payload, f"yield_strength_{view}", None)
        cWidth = getattr(payload, f"coil_width_{view}", None)
        cWeight = getattr(payload, f"coil_weight_{view}", None)
        cID = getattr(payload, f"coil_id_{view}", None)

        # Calculate specifications for current variant
        computed = calculate_variant(mType, thickness, yld, cWidth, cWeight, cID)
        
        # Store results with variant-specific keys
        results[f"min_bend_radius_{view}"] = computed["min_bend_radius"]
        results[f"min_loop_length_{view}"] = computed["min_loop_length"]
        results[f"coil_od_calculated_{view}"] = computed["coil_od_calculated"]
    try:
        append_to_json_list(
            label="material_specs", 
            data=results, 
            reference_number=rfq_state.reference, 
            directory=JSON_FILE_PATH
        )
    except Exception as e:
        # Return error if save operation fails
        return {"error": f"Failed to save results: {str(e)}"}

    return results

@router.get("/load")
def load_material_specs() -> Dict[str, Any]:
    """
    Load previously calculated material specifications from JSON storage.
    
    Returns: \n
        Dict[str, Any]: Response dictionary containing:
            - Success: {"count": int, "entries": [list_of_results]}
            - No data found: {"count": 0, "entries": []}
            - Error: {"error": "error_description"}
            
    Error Handling: \n
        - FileNotFoundError: Returns empty result set with count 0
        - Other exceptions: Returns error message
    """
    
    try:
        # Attempt to load data for current RFQ reference
        data = load_json_list(
            label="material_specs", 
            reference_number=rfq_state.reference, 
            directory=JSON_FILE_PATH
        )
        
        # Return successful result with count and data
        return {"count": len(data), "entries": data}
        
    except FileNotFoundError:
        # No previous data exists for this reference - return empty result
        return {"count": 0, "entries": []}
        
    except Exception as e:
        # Other errors - return error message
        return {"error": str(e)}