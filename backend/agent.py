"""
Agent pipeline: Classify -> Route -> Explain
"""

import os
import json
import traceback
from dotenv import load_dotenv
from reference_ranges import get_reference_range

load_dotenv()

# -------------------------------
# Initialize Anthropic Client
# -------------------------------

try:
    import anthropic

    _api_key = os.getenv("ANTHROPIC_API_KEY")

    print("=" * 50)
    print("Loading Anthropic...")
    print("API Key Present:", bool(_api_key))
    print("=" * 50)

    if _api_key:
        _client = anthropic.Anthropic(api_key=_api_key)
    else:
        _client = None

except Exception as e:
    print("Anthropic Initialization Error:", e)
    _client = None


# -------------------------------
# Classification
# -------------------------------

def classify(test_name: str, value: float):
    """
    Deterministic classification against reference range.
    """

    ref = get_reference_range(test_name)

    low = ref.get("low")
    high = ref.get("high")

    if low is None or high is None:
        return "Warning", ref, "no_reference_range"

    if value < low or value > high:

        span = max(high - low, 1e-6)

        deviation = max(low - value, value - high) / span

        status = "Critical" if deviation > 0.5 else "Warning"

    else:

        status = "Normal"

    return status, ref, None


# -------------------------------
# Fallback Explanation
# -------------------------------

def _fallback_explanation(test_name, value, unit, status, ref):

    low = ref.get("low")
    high = ref.get("high")

    if status == "Normal":

        explanation = (
            f"{test_name.title()} of {value} "
            f"{unit or ref.get('unit') or ''} "
            f"falls within the normal reference range "
            f"({low}-{high})."
        )

        next_steps = [
            "No action needed.",
            "Continue routine monitoring."
        ]

    else:

        direction = "below" if value < low else "above"

        explanation = (
            f"{test_name.title()} of {value} "
            f"{unit or ref.get('unit') or ''} is "
            f"{direction} the reference range "
            f"({low}-{high}). "
            f"This may require clinical evaluation."
        )

        if status == "Critical":

            next_steps = [
                "Seek urgent physician review.",
                "Repeat testing immediately."
            ]

        else:

            next_steps = [
                "Schedule physician review.",
                "Repeat testing if recommended."
            ]

    return explanation, next_steps


# -------------------------------
# LLM Explanation
# -------------------------------

def explain(test_name, value, unit, status, ref):

    print("\n" + "=" * 60)
    print("EXPLAIN FUNCTION CALLED")
    print("Test:", test_name)
    print("Value:", value)
    print("Status:", status)
    print("=" * 60)

    if _client is None:

        print("Using fallback because client is None.")

        return _fallback_explanation(
            test_name,
            value,
            unit,
            status,
            ref
        )

    prompt = f"""
You are an experienced physician.

Explain this laboratory result.

Laboratory Test:
{test_name}

Patient Value:
{value} {unit or ref.get("unit") or ""}

Reference Range:
{ref.get("low")} - {ref.get("high")} {ref.get("unit") or ""}

Classification:
{status}

Instructions:

1. Explain what this laboratory test measures.
2. Explain why THIS value is normal or abnormal.
3. Mention common medical causes.
4. Mention whether it is mild, moderate or severe.
5. Give two follow-up recommendations.

Return ONLY JSON.

Example:

{{
    "explanation":"....",
    "next_steps":[
        "...",
        "..."
    ]
}}
"""

    try:

        print("Calling Claude...")

        response = _client.messages.create(

            model="claude-sonnet-5",

            max_tokens=500,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw = ""

        for block in response.content:

            if getattr(block, "type", "") == "text":
                raw += block.text

        raw = raw.strip()

        print("Claude Raw Response:")
        print(raw)

        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()

        data = json.loads(raw)

        return (
            data.get("explanation", ""),
            data.get("next_steps", [])
        )

    except Exception as e:

        print("=" * 60)
        print("CLAUDE API ERROR")
        traceback.print_exc()
        print("=" * 60)

        return (
            f"Claude Error: {str(e)}",
            ["Check backend logs."]
        )


# -------------------------------
# Complete Pipeline
# -------------------------------

def process_lab(test_name, value, unit=None):

    try:

        status, ref, warning = classify(
            test_name,
            value
        )

        explanation, next_steps = explain(
            test_name,
            value,
            unit,
            status,
            ref
        )

        return {

            "status": status,

            "reference_low": ref.get("low"),

            "reference_high": ref.get("high"),

            "explanation": explanation,

            "next_steps": next_steps,

            "error": None,
        }

    except Exception as e:

        traceback.print_exc()

        return {

            "status": "Error",

            "reference_low": None,

            "reference_high": None,

            "explanation": "",

            "next_steps": [],

            "error": str(e),
        }