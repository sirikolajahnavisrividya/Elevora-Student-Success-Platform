from pydantic import BaseModel, Field

class StudentFeatures(BaseModel):
    attendance: float = Field(..., ge=0, le=100)
    internal_marks: float = Field(..., ge=0, le=100)
    assignment_score: float = Field(..., ge=0, le=100)
    quiz_score: float = Field(..., ge=0, le=100)
    previous_cgpa: float = Field(..., ge=0, le=10)
    backlogs: int = Field(..., ge=0, le=20)
    study_hours: float = Field(..., ge=0, le=24)

class PredictionResponse(BaseModel):
    risk_level: str
    risk_probability: float
    recommendation: str
    factors: list[str]
    model_version: str

class StudentRecord(StudentFeatures):
    student_id: str
    semester: int = Field(..., ge=1, le=8)
