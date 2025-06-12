"""
Utility functions for handling JSON files with labeled data.

"""

import json
import os
from typing import Any, Optional


def append_to_json_list(label: str, data: dict, reference_number: str, directory: str = "./outputs") -> str:
    """
    Appends or updates labeled data under a reference-number-named JSON file.

    Args:
        label (str): Key to store the data under (e.g., "tddbhd").
        data (dict): The result data to store.
        reference_number (str): Used as the filename.
        directory (str): Target output directory.

    Returns:
        str: Full path to the updated JSON file.
    """
    os.makedirs(directory, exist_ok=True)
    full_path = os.path.join(directory, f"{reference_number}.json")

    if os.path.exists(full_path):
        try:
            with open(full_path, "r") as f:
                content = json.load(f)
        except json.JSONDecodeError:
            content = {}
    else:
        content = {}

    content[label] = data

    with open(full_path, "w") as f:
        json.dump(content, f, indent=4)

    return full_path


def load_json_list(label: str, reference_number: str, directory: str = "./outputs") -> dict:
    """
    Loads a specific labeled block from a JSON file named after the reference number.

    Args:
        label (str): The label key to extract (e.g., "tddbhd").
        reference_number (str): Name of the file (without extension).
        directory (str): Directory where the JSON file resides.

    Returns:
        dict: The labeled section of the JSON.

    Raises:
        FileNotFoundError: If the reference JSON does not exist.
        KeyError: If the label is not found in the file.
    """
    file_path = os.path.join(directory, f"{reference_number}.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File for reference '{reference_number}' not found.")

    with open(file_path, "r") as f:
        content = json.load(f)

    if label not in content:
        raise KeyError(f"Label '{label}' not found in file '{reference_number}.json'.")

    return content[label]
