from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class ServiceQuestion(SQLModel, table=True):
    QuestionID: Optional[str] = Field(default=None, primary_key=True)
    Question: str
    Sequence: int
