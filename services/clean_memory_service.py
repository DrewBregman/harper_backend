"""Service for cleaning memory data.

Removes unwanted fields:
  - "phone_events" (top-level)
  - "md" in "company"
  - "facts" in "company.json"
"""

import copy
from typing import Dict, Any

def clean_memory(memory_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a copy of the memory_data dict but:
      1) Removes the entire "phone_events" key/value.
      2) Removes the "md" field from the "company" object.
      3) Removes the "facts" array under "company.json".
    """
    cleaned = copy.deepcopy(memory_data)

    # 1. Remove phone_events completely if it exists
    if "phone_events" in cleaned:
        del cleaned["phone_events"]

    # 2. Remove "md" under "company"
    if "company" in cleaned and "md" in cleaned["company"]:
        del cleaned["company"]["md"]

    # 3. Remove "facts" array under company.json
    #    i.e. company["json"]["facts"]
    if "company" in cleaned:
        company_section = cleaned["company"]
        if "json" in company_section and "facts" in company_section["json"]:
            del company_section["json"]["facts"]

    return cleaned