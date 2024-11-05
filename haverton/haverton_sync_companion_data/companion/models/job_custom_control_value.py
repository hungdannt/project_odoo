from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class JobCustomControlValue(SQLModel, table=True):
    """
    Used for ContractHouseDesign with CustomControlID = '820AA85C-E8F7-4102-A40A-8B2A138994E5'
    """
    JobID: Optional[str] = Field(default=None, primary_key=True)
    CustomControlID: str
    Text: str
