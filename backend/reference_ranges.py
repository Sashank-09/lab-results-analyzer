"""
Hardcoded reference ranges for common lab tests.
If a test isn't found here, reference_range_lookup() is called as a
fallback "tool" the agent can invoke (simulated lookup / can be wired
to a real API such as LOINC in production).
"""

REFERENCE_RANGES = {
    "hemoglobin":       {"low": 13.5, "high": 17.5, "unit": "g/dL"},
    "wbc":              {"low": 4.5,  "high": 11.0, "unit": "10^3/uL"},
    "platelets":        {"low": 150,  "high": 450,  "unit": "10^3/uL"},
    "glucose":          {"low": 70,   "high": 100,  "unit": "mg/dL"},
    "creatinine":       {"low": 0.6,  "high": 1.3,  "unit": "mg/dL"},
    "sodium":           {"low": 135,  "high": 145,  "unit": "mmol/L"},
    "potassium":        {"low": 3.5,  "high": 5.1,  "unit": "mmol/L"},
    "alt":              {"low": 7,    "high": 56,   "unit": "U/L"},
    "ast":              {"low": 10,   "high": 40,   "unit": "U/L"},
    "cholesterol_total":{"low": 0,    "high": 200,  "unit": "mg/dL"},
    "hdl":              {"low": 40,   "high": 60,   "unit": "mg/dL"},
    "ldl":              {"low": 0,    "high": 100,  "unit": "mg/dL"},
    "tsh":              {"low": 0.4,  "high": 4.0,  "unit": "mIU/L"},
    "hba1c":            {"low": 4.0,  "high": 5.6,  "unit": "%"},
    "bun":              {"low": 7,    "high": 20,   "unit": "mg/dL"},
}


def normalize_test_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def reference_range_lookup(test_name: str):
    """
    Optional 'tool' the agent calls when a test isn't in the hardcoded
    dict. In this assignment it simulates an external lookup service;
    swap the body for a real API call (e.g. LOINC) in production.
    """
    key = normalize_test_name(test_name)
    if key in REFERENCE_RANGES:
        return REFERENCE_RANGES[key]

    # Simulated fallback lookup for unknown tests so the pipeline
    # never silently fails during a demo.
    return {"low": None, "high": None, "unit": None, "source": "unresolved"}


def get_reference_range(test_name: str):
    key = normalize_test_name(test_name)
    if key in REFERENCE_RANGES:
        return REFERENCE_RANGES[key]
    return reference_range_lookup(test_name)
