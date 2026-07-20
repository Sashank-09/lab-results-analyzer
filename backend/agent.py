"""
Agent pipeline:
Classify -> Route -> Explain (Gemini)
"""

import os
import json
import traceback

from dotenv import load_dotenv
from google import genai

from reference_ranges import get_reference_range

load_dotenv()

# --------------------------------------------------------
# Gemini Client
# --------------------------------------------------------

_client = None

try:
    api_key = os.getenv("GEMINI_API_KEY")

    print("=" * 60)
    print("Loading Gemini...")
    print("API Key Present:", bool(api_key))
    print("=" * 60)

    if api_key:
        _client = genai.Client(api_key=api_key)

except Exception as e:
    print("Gemini Initialization Error:", e)
    _client = None


# --------------------------------------------------------
# Classification
# --------------------------------------------------------

def classify(test_name: str, value: float):

    ref = get_reference_range(test_name)

    low = ref.get("low")
    high = ref.get("high")

    if low is None or high is None:
        return "Warning", ref, "no_reference_range"

    if value < low or value > high:

        span = max(high - low, 1e-6)

        deviation = max(low - value, value - high) / span

        if deviation > 0.5:
            status = "Critical"
        else:
            status = "Warning"

    else:
        status = "Normal"

    return status, ref, None


# --------------------------------------------------------
# Fallback Explanation
# --------------------------------------------------------

def _fallback_explanation(test_name, value, unit, status, ref):

    low = ref.get("low")
    high = ref.get("high")

    if status == "Normal":

        explanation = (
            f"{test_name.title()} ({value} {unit or ref.get('unit') or ''}) "
            f"is within the normal reference range "
            f"({low}-{high})."
        )

        steps = [
            "No immediate action required.",
            "Continue routine monitoring."
        ]

    else:

        direction = "below" if value < low else "above"

        explanation = (
            f"{test_name.title()} ({value} {unit or ref.get('unit') or ''}) "
            f"is {direction} the reference range "
            f"({low}-{high}). "
            f"This result should be reviewed by a physician."
        )

        if status == "Critical":

            steps = [
                "Seek urgent medical review.",
                "Repeat the laboratory test promptly."
            ]

        else:

            steps = [
                "Consult your physician.",
                "Repeat testing if clinically indicated."
            ]

    return explanation, steps

# --------------------------------------------------------
# AI Explanation (Gemini)
# --------------------------------------------------------

def explain(test_name, value, unit, status, ref):

    if _client is None:
        return _fallback_explanation(
            test_name,
            value,
            unit,
            status,
            ref
        )

    prompt = f"""
You are an experienced physician.

Analyze the following laboratory result.

Test Name:
{test_name}

Patient Value:
{value} {unit or ref.get("unit")}

Reference Range:
{ref.get("low")} - {ref.get("high")} {ref.get("unit")}

Classification:
{status}

Return ONLY valid JSON.

Required format:

{{
    "explanation":"A patient-friendly explanation in 3-5 sentences.",
    "next_steps":[
        "step 1",
        "step 2"
    ]
}}

Rules:

- Explain what the test measures.
- Explain why this result is normal or abnormal.
- Mention common causes.
- Do NOT diagnose diseases.
- Keep language simple.
- Do NOT use markdown.
- Output JSON only.
"""

    try:

        response = _client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown fences if Gemini adds them
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        data = json.loads(text)

        explanation = data.get(
            "explanation",
            "No explanation available."
        )

        next_steps = data.get(
            "next_steps",
            []
        )

        if not isinstance(next_steps, list):
            next_steps = [str(next_steps)]

        return explanation, next_steps

    except Exception as e:

        print("=" * 60)
        print("Gemini Error")
        traceback.print_exc()
        print("=" * 60)

        return _fallback_explanation(
            test_name,
            value,
            unit,
            status,
            ref
        )
    
# --------------------------------------------------------
# Main Pipeline
# --------------------------------------------------------

def process_lab(test_name, value, unit=None):
    """
    Complete pipeline:
        1. Classify the lab result
        2. Generate explanation
        3. Return structured response
    """

    try:

        # Step 1: Classify
        status, ref, error = classify(test_name, value)

        if error:
            return {
                "test_name": test_name,
                "value": value,
                "unit": unit,
                "status": "Error",
                "reference_range": ref,
                "explanation": "Reference range not available for this laboratory test.",
                "next_steps": [
                    "Consult a healthcare professional.",
                    "Verify the laboratory test name."
                ]
            }

        # Step 2: Generate explanation
        explanation, next_steps = explain(
            test_name=test_name,
            value=value,
            unit=unit,
            status=status,
            ref=ref
        )

        # Step 3: Return response
        return {
            "test_name": test_name,
            "value": value,
            "unit": unit or ref.get("unit"),
            "status": status,
            "reference_range": ref,
            "explanation": explanation,
            "next_steps": next_steps
        }

    except Exception:

        traceback.print_exc()

        return {
            "test_name": test_name,
            "value": value,
            "unit": unit,
            "status": "Error",
            "reference_range": {},
            "explanation": "An unexpected error occurred while processing this laboratory result.",
            "next_steps": [
                "Try again later.",
                "Contact support if the issue persists."
            ]
        }