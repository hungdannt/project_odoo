from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class JobActivityQuestionAnswer(SQLModel, table=True):
    QuestionID: Optional[str] = Field(default=None, primary_key=True)
    ActivityID: Optional[str] = Field(default=None, primary_key=True)
    Completed: bool
    NotApplicable: bool
    Note: str
