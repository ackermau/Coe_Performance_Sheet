import argparse
import json
from utils.database import get_default_repository
from utils.shared import rfq_state
from models import (
    RFQ, FPMInput, MaterialSpecsPayload, TDDBHDInput, ReelDriveInput, StrUtilityInput, RollStrBackbendInput,
    FeedInput, FeedWPullThruInput, AllenBradleyInput, HydShearInput, ZigZagInput
)
# Calculation imports
from calculations.rfq import calculate_fpm
from calculations.material_specs import calculate_specs
from calculations.tddbhd import calculate_tbdbhd
from calculations.reel_drive import calculate_reeldrive
from calculations.str_utility import calculate_str_utility
from calculations.rolls.roll_str_backbend import calculate_roll_str_backbend
from calculations.feeds.sigma_five_feed import calculate_sigma_five
from calculations.feeds.sigma_five_feed_with_pt import calculate_sigma_five_pt
from calculations.feeds.allen_bradley_mpl_feed import calculate_allen_bradley
from calculations.shears.single_rake_hyd_shear import calculate_single_rake_hyd_shear
from calculations.shears.bow_tie_hyd_shear import calculate_bow_tie_hyd_shear
from calculations.zig_zag import calculate_zig_zag

# Map calculation names to (input model, calculation function)
CALCULATIONS = [
    ("rfq", RFQ, calculate_fpm),
    ("material_specs", MaterialSpecsPayload, calculate_specs),
    ("tddbhd", TDDBHDInput, calculate_tbdbhd),
    ("reel_drive", ReelDriveInput, calculate_reeldrive),
    ("str_utility", StrUtilityInput, calculate_str_utility),
    ("roll_str_backbend", RollStrBackbendInput, calculate_roll_str_backbend),
    ("sigma_five_feed", FeedInput, calculate_sigma_five),
    ("sigma_five_feed_with_pt", FeedWPullThruInput, calculate_sigma_five_pt),
    ("allen_bradley_mpl_feed", AllenBradleyInput, calculate_allen_bradley),
    ("single_rake_hyd_shear", HydShearInput, calculate_single_rake_hyd_shear),
    ("bow_tie_hyd_shear", HydShearInput, calculate_bow_tie_hyd_shear),
    ("zig_zag", ZigZagInput, calculate_zig_zag),
]

def prompt_for_data(model_class, reference=None, input_data=None):
    data = {}
    for field in model_class.__fields__:
        if field == "reference" and reference is not None:
            data[field] = reference
            continue
        if input_data and field in input_data:
            data[field] = input_data[field]
            continue
        val = input(f"Enter value for {field} (leave blank for None): ")
        if val == "":
            data[field] = None
        else:
            typ = model_class.__fields__[field].type_
            try:
                if typ == int:
                    data[field] = int(val)
                elif typ == float:
                    data[field] = float(val)
                elif typ == bool:
                    data[field] = val.lower() in ("1", "true", "yes", "y")
                else:
                    data[field] = val
            except Exception:
                data[field] = val
    return model_class(**data)

def main():
    parser = argparse.ArgumentParser(description="COE Performance Sheet Main Entrypoint")
    parser.add_argument("reference", type=str, help="Reference number")
    parser.add_argument("--action", type=str, choices=["upsert", "get", "delete"], default="upsert", help="CRUD action to perform")
    parser.add_argument("--input", type=str, help="Path to JSON file with input data")
    args = parser.parse_args()
    reference = args.reference
    rfq_state.reference = reference
    repo = get_default_repository()

    input_data = None
    if args.input:
        with open(args.input) as f:
            input_data = json.load(f)

    if args.action == "get":
        result = repo.get(reference)
        if result:
            print(f"Data for reference {reference}:")
            print(result)
        else:
            print(f"No data found for reference {reference}.")
        return

    if args.action == "delete":
        deleted = repo.delete(reference)
        if deleted:
            print(f"Deleted data for reference {reference}.")
        else:
            print(f"No data found for reference {reference} to delete.")
        return

    # Default: upsert (create or update all calculations)
    existing = repo.get(reference)
    if existing:
        print(f"Found existing data for reference {reference}. Updating calculations...")
        for name, model_class, calc_func in CALCULATIONS:
            print(f"Updating {name}...")
            data_dict = existing['data'].get(name)
            if data_dict:
                obj = model_class(**data_dict)
            else:
                obj = prompt_for_data(model_class, reference, input_data.get(name) if input_data else None)
            result = calc_func(obj)
            repo.upsert(reference, {name: result})
            print(f"{name} updated.")
    else:
        print(f"No data found for reference {reference}. Creating new entry...")
        for name, model_class, calc_func in CALCULATIONS:
            print(f"Creating {name}...")
            obj = prompt_for_data(model_class, reference, input_data.get(name) if input_data else None)
            result = calc_func(obj)
            repo.upsert(reference, {name: result})
            print(f"{name} created.")
    print("All calculations complete.")

if __name__ == "__main__":
    main() 