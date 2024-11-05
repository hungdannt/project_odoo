from typing import Optional

from sqlmodel import Field, SQLModel


class Address(SQLModel, table=True):
    AddressID: Optional[str] = Field(default=None, primary_key=True)
    Address1: str
    Address2: str
    Suburb: str
    State: str
    Postcode: str
    Country: str
    LotNumber: str
    DpLotNumber: str
    BlockNumber: str
    SectionNumber: str
    PoBoxNumber: str
    PropertyName: str
    MapFriendlyAddress: str
