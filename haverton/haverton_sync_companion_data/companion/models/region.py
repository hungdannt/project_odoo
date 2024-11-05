from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class Region(SQLModel, table=True):
    RegionID: Optional[str] = Field(default=None, primary_key=True)
    Description: str
    ParentRegionID: str
    IsDefaultJobRegion: bool
    IsDefaultServiceProviderRegion: bool
    Active: bool
