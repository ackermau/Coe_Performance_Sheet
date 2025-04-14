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
lookup_reels = LOOKUP_DATA.get("lookup_reels", {})
lookup_friction = LOOKUP_DATA.get("lookup_friction", {})

def get_material_density(material: str) -> float:
    """Return the density for a given material from the JSON lookup."""
    material_key = material.upper()
    try:
        return lookup_material[material_key]["density"]
    except KeyError:
        raise ValueError(f"Unknown material: {material}")

def get_reel_max_weight(reel_model: str) -> int:
    """Return the maximum weight for a given reel model from the JSON lookup."""
    reel_model_key = reel_model.upper()
    try:
        return lookup_reels[reel_model_key]
    except KeyError:
        raise ValueError(f"Unknown reel model: {reel_model}")

def get_friction(key: str = "DEFAULT") -> float:
    """Return a friction value from the JSON lookup."""
    key = key.upper()
    try:
        return lookup_friction[key]
    except KeyError:
        raise ValueError(f"Unknown friction key: {key}")

def get_material_data(material: str) -> dict:
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
