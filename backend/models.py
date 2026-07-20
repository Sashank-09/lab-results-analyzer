from pydantic import BaseModel, Field
from typing import List, Optional


class LabResultIn(BaseModel):
    test_name: str
    value: float
    unit: Optional[str] = None
    patient_id: Optional[str] = None


class AnalyzeRequest(BaseModel):
    labs: List[LabResultIn]


class ClassifiedResult(BaseModel):
    test_name: str
    value: float
    unit: Optional[str] = None
    patient_id: Optional[str] = None
    status: str                      # Normal | Warning | Critical
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    explanation: str
    next_steps: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class AnalyzeResponse(BaseModel):
    critical: List[ClassifiedResult]
    warning: List[ClassifiedResult]
    normal: List[ClassifiedResult]
    errors: List[ClassifiedResult]
