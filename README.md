# Clinical Lab Results Analyzer

Full-stack app that classifies clinical lab results as **Normal / Warning / Critical**,
explains *why* each result was flagged (Explainable AI), and suggests next steps —
built for the GenAI + Full-Stack assignment.

## Architecture

```
┌─────────────┐      POST /analyze_labs      ┌──────────────────┐
│   React     │ ───────────────────────────▶ │  FastAPI backend │
│  (frontend) │ ◀─────────────────────────── │                  │
└─────────────┘        JSON response          └────────┬─────────┘
                                                         │
                                            Classify → Route → Explain
                                                         │
                                         ┌───────────────┴───────────────┐
                                         │                               │
                                reference_ranges.py               Claude API (LLM)
                              (local dict + fallback tool)      (clinical explanation)
```

**Agent logic (Classify → Route → Explain)** lives in `backend/agent.py`:
1. **Classify** — compares the numeric value to a reference range (local, deterministic,
   fast — no LLM call needed for arithmetic). If a test isn't in the hardcoded dict,
   `reference_range_lookup()` in `reference_ranges.py` is called as a fallback tool.
2. **Route** — `main.py` groups classified results into `critical` / `warning` / `normal` / `errors`
   buckets, critical-first.
3. **Explain** — calls the LLM (Claude) with the value, reference range, and classification,
   and asks for a short clinical explanation plus next steps — grounded in the *actual*
   deviation, not a generic "abnormal" label. If no API key is set, a deterministic
   fallback explanation is used so the app still runs end-to-end for a demo.

## AI Provider Chosen

**Claude** (`claude-sonnet-4-6`), via the official `anthropic` Python SDK. Chosen for
free credits, strong structured-output adherence (JSON-only responses), and reliable
clinical-reasoning quality. Swapping providers only requires editing `explain()` in
`backend/agent.py`.

## Setup

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then add your ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start                   # runs on http://localhost:3000
```

The frontend calls `http://localhost:8000` by default (see `src/api.js`).
Override with `REACT_APP_API_BASE` in a `.env` file inside `frontend/` if needed.

## How to Test

1. Start the backend and frontend (above).
2. Open `http://localhost:3000`.
3. Upload one of the CSVs in `/test_data`:
   - `patient_001_normal_panel.csv` — all-normal panel
   - `patient_002_mixed_warnings.csv` — mixed warning-range results
   - `patient_003_critical_case.csv` — critical values + one intentionally
     malformed row (missing test name) to exercise error handling
4. Results render grouped by severity with color-coded badges, AI explanations,
   and suggested next steps.

Or hit the API directly:
```bash
curl -X POST http://localhost:8000/analyze_labs \
  -H "Content-Type: application/json" \
  -d '{"labs":[{"test_name":"Glucose","value":410,"unit":"mg/dL","patient_id":"P003"}]}'
```

## Project Structure
```
backend/
  main.py               FastAPI app, POST /analyze_labs, routing
  agent.py              Classify -> Explain pipeline, LLM call
  reference_ranges.py   Hardcoded ranges + fallback lookup tool
  models.py             Pydantic request/response schemas
frontend/
  src/App.jsx
  src/components/LabInput.jsx        form + CSV upload
  src/components/ResultsDisplay.jsx  severity-grouped results
  src/components/SeverityBadge.jsx   color-coded status badge
test_data/               3 synthetic CSVs
```

## Error Handling
- Missing/blank test name → routed to `errors` bucket with a clear message.
- Missing numeric value → routed to `errors` bucket.
- Unknown test name → falls back to `reference_range_lookup()`; if still
  unresolved, classified as `Warning` pending manual reference range entry.
- LLM call failure (no API key, network, malformed response) → deterministic
  fallback explanation, so the pipeline never hard-crashes.

## Notes / Scope
- 6 tests covered in `reference_ranges.py` (assignment requires ≥5).
- Explainability: every flagged result states the specific reference range and
  which direction/magnitude it deviated by, not just "abnormal."
