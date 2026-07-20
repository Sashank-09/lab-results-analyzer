from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest, AnalyzeResponse, ClassifiedResult
from agent import process_lab

app = FastAPI(title="Clinical Lab Results Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo only. Restrict in production.
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "clinical-lab-results-analyzer"
    }


@app.post("/analyze_labs", response_model=AnalyzeResponse)
def analyze_labs(req: AnalyzeRequest):

    if not req.labs:
        raise HTTPException(
            status_code=400,
            detail="No lab results provided."
        )

    critical = []
    warning = []
    normal = []
    errors = []

    for lab in req.labs:

        # -----------------------------
        # Validate input
        # -----------------------------
        if not lab.test_name or not lab.test_name.strip():
            errors.append(
                ClassifiedResult(
                    test_name=lab.test_name or "unknown",
                    value=lab.value,
                    unit=lab.unit,
                    patient_id=lab.patient_id,
                    status="Error",
                    reference_low=None,
                    reference_high=None,
                    explanation="",
                    next_steps=[],
                    error="Missing laboratory test name."
                )
            )
            continue

        if lab.value is None:
            errors.append(
                ClassifiedResult(
                    test_name=lab.test_name,
                    value=0,
                    unit=lab.unit,
                    patient_id=lab.patient_id,
                    status="Error",
                    reference_low=None,
                    reference_high=None,
                    explanation="",
                    next_steps=[],
                    error="Missing laboratory value."
                )
            )
            continue

        # -----------------------------
        # AI Pipeline
        # -----------------------------
        result = process_lab(
            lab.test_name,
            lab.value,
            lab.unit
        )

        classified = ClassifiedResult(
            test_name=lab.test_name,
            value=lab.value,
            unit=lab.unit,
            patient_id=lab.patient_id,
            status=result["status"],
            reference_low=result["reference_range"].get("low"),
            reference_high=result["reference_range"].get("high"),
            explanation=result["explanation"],
            next_steps=result["next_steps"],
            error=None if result["status"] != "Error" else result["explanation"],
        )

        # -----------------------------
        # Route by severity
        # -----------------------------
        if result["status"] == "Critical":
            critical.append(classified)

        elif result["status"] == "Warning":
            warning.append(classified)

        elif result["status"] == "Normal":
            normal.append(classified)

        else:
            errors.append(classified)

    # ==========================================
    # IMPORTANT:
    # Return AFTER processing ALL lab results
    # ==========================================
    return AnalyzeResponse(
        critical=critical,
        warning=warning,
        normal=normal,
        errors=errors,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )