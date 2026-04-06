from pydantic import BaseModel
from typing import Optional

class Email(BaseModel):
    subject: str
    body: str
    sender: str

class Observation(BaseModel):
    email: Email
    step_count: int

class Action(BaseModel):
    label: str

class Reward(BaseModel):
    score: float
    reason: Optional[str] = None


class EmailAnalysis(BaseModel):
    category: str
    main_subject: str
    confidence: float
    reason: Optional[str] = None