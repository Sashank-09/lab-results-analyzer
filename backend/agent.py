"""
Agent pipeline: Classify -> Route -> Explain
"""

import os
import json
from dotenv import load_dotenv
from reference_ranges import get_reference_range, normalize_test_name

load_dotenv()  # reads backend/.env into os.environ -- this was missing before

USE_LLM = True
try:
    import anthropic

    _api_key = os.getenv("ANTHROPIC_API_KEY")

    print("================================")
    print("Loading Anthropic...")
    print("API Key Present:", bool(_api_key))
    print("================================")

    if _api_key:
        _client = anthropic.Anthropic(api_key=_api_key)
    else:
        _client = None

except Exception as e:
    print("Anthropic Initialization Error:", e)
    _client = None


def classify(test_name: str, value: float):
    """Deterministic classification against reference range."""
    ref = get_reference_range(test_name)
    low, high = ref.get("low"), ref.get("high")

    if low is None or high is None:
        return "Warning", ref, "no_reference_range"

    if value < low or value > high:
        span = max(high - low, 1e-6)
        deviation = max(low - value, value - high) / span
        status = "Critical" if deviation > 0.5 else "Warning"
    else:
        status = "Normal"

    return status, ref, None


def _fallback_explanation(test_name, value, unit, status, ref):
    low, high = ref.get("low"), ref.get("high")
    if status == "Normal":
        text = (f"{test_name.title()} of {value} {unit or ref.get('unit') or ''} "
                f"falls within the normal reference range ({low}-{high}).")
        steps = ["No action needed.", "Continue routine monitoring."]
    else:
        direction = "below" if low is not None and value < low else "above"
        text = (f"{test_name.title()} of {value} {unit or ref.get('unit') or ''} is "
                f"{direction} the reference range ({low}-{high}), which may indicate "
                f"a clinically significant abnormality requiring review.")
        steps = (["Escalate for urgent physician review.", "Consider repeat testing to confirm."]
                  if status == "Critical" else
                  ["Flag for physician review.", "Recommend follow-up testing."])
    return text, steps


def explain(test_name: str, value: float, unit: str, status: str, ref: dict):
    """
    Uses Claude to generate a clinical explanation.
    Falls back only if Claude fails.
    """

    print("\n" + "=" * 60)
    print("EXPLAIN FUNCTION CALLED")
    print(f"Test: {test_name}")
    print(f"Value: {value}")
    print(f"Status: {status}")

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    print("API Key Present:", bool(api_key))
    print("Client Created:", _client is not None)
    print("=" * 60)

    if _client is None or not api_key:
        print(">>> USING FALLBACK (Missing API Key or Client)")
        return _fallback_explanation(test_name, value, unit, status, ref)

    prompt = f"""
You are an experienced physician.

Explain the following laboratory result.

Laboratory Test:
{test_name}

Patient Value:
{value} {unit or ref.get('unit') or ''}

Reference Range:
{ref.get('low')} - {ref.get('high')} {ref.get('unit') or ''}

Classification:
{status}

Instructions:

1. Explain what this laboratory test measures.
2. Explain why THIS patient's value is abnormal or normal.
3. Mention likely medical causes.
4. Mention whether the abnormality is mild, moderate, or severe.
5. Give two short follow-up recommendations.

Return ONLY valid JSON.

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

        print(">>> CALLING CLAUDE API")

        response = _client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        print(">>> CLAUDE RESPONSE RECEIVED")

        raw = "".join(
            block.text
            for block in response.content
            if getattr(block, "type", "") == "text"
        ).strip()

        print("Raw Response:")
        print(raw)

        raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)

        print(">>> JSON PARSED SUCCESSFULLY")

        return (
            data.get("explanation", ""),
            data.get("next_steps", [])
        )

    except Exception as e:

        import traceback

        print("\n>>> CLAUDE API FAILED <<<")
        traceback.print_exc()

        print("Using fallback explanation.\n")

        return _fallback_explanation(
            test_name,
            value,
            unit,
            status,
            ref
        )