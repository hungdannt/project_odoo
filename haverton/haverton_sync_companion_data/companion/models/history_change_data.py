from typing import Optional

from sqlmodel import Field, SQLModel


class HistoryChangeData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    table_name: str
    action_name: str
    data_before_change: str
    data_after_change: str
    time_change: str
    status: str
    note: str
