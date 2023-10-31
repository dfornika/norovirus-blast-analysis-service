from pydantic import BaseModel
from typing import List, Optional


class AnalysisSubmissionRequest(BaseModel):
    """
    """
    sequences: List[dict]

    class Config:
        from_attributes = True


class AnalysisSubmissionResponse(BaseModel):
    """
    """
    analysis_uuid: str
    status: str

    class Config:
        from_attributes = True


