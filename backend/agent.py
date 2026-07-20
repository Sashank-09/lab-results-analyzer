"""
Agent pipeline: Classify -> Route -> Explain

This mirrors a simple deterministic-classification + LLM-explanation
agent, which is the pattern the assignment asks for:
  1. Classify: compare numeric value to reference range (local, fast,
     deterministic -- no need to burn LLM tokens on arithmetic).
  2. Route: group by severity (handled in main.py after classify).
  3. Explain: call the LLM to turn the raw classification into a
     clinically meaningful, *explainable* narrative + next steps.
"""

import os
import json
from reference_ranges import get_reference_range, normalize_test_name

USE_LLM = True
try:
    import anthropic
    _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
except Exception:
    _client = None


def classify(test_name: str, value: float):
    """Deterministic classification against reference range."""
    ref = get_reference_range(test_name)
    low, high = ref.get("low"), ref.get("high")

    if low is None or high is None:
        return "Warning", ref, "no_reference_range"

    if value < low or value > high:
        # How far outside the range determines Critical vs Warning.
        span = max(high - low, 1e-6)
        deviation = max(low - value, value - high) / span
        status = "Critical" if deviation > 0.5 else "Warning"
    else:
        status = "Normal"

    return status, ref, None


def _fallback_explanation(test_name, value, unit, status, ref):
    """Used if no API key / LLM call fails, so the demo still runs."""
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
    Calls the LLM to produce a clinically relevant, explainable
    justification for the classification, plus suggested next steps.
    Falls back to a deterministic explanation if the LLM is unavailable,
    so the app never crashes during a demo/grading run.
    """
    if _client is None or not os.environ.get("ANTHROPIC_API_KEY"):
        return _fallback_explanation(test_name, value, unit, status, ref)

    prompt = f"""You are a clinical decision-support assistant. Explain a lab result
using Explainable AI principles: be specific about WHY this value was flagged,
not just that it is abnormal.

Test: {test_name}
Value: {value} {unit or ref.get('unit') or ''}
Reference range: {ref.get('low')} - {ref.get('high')} {ref.get('unit') or ''}
Classification: {status}

Respond ONLY with JSON, no other text, in this exact shape:
{{"explanation": "2-3 sentence clinically relevant explanation of why this value was flagged and what it means",
"next_steps": ["short actionable next step", "short actionable next step"]}}
"""

    try:
        resp = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "".join(b.text for b in resp.content if b.type == "text").strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        return data.get("explanation", ""), data.get("next_steps", [])
    except Exception:
        return _fallback_explanation(test_name, value, unit, status, ref)


def process_lab(test_name: str, value: float, unit: str = None):
    """Full Classify -> Explain pipeline for a single lab result."""
    try:
        status, ref, warning = classify(test_name, value)
        explanation, next_steps = explain(test_name, value, unit, status, ref)
        return {
            "status": status,
            "reference_low": ref.get("low"),
            "reference_high": ref.get("high"),
            "explanation": explanation,
            "next_steps": next_steps,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "Error",
            "reference_low": None,
            "reference_high": None,
            "explanation": "",
            "next_steps": [],
            "error": str(e),
        }
