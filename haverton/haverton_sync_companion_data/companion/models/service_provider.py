from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class ServiceProvider(SQLModel, table=True):
    ServiceProviderID: Optional[str] = Field(default=None, primary_key=True)
    OrganisationName: str
    OrganisationTradingAsName: str
    EntityCode: str
    ABN: str
    WorkUrl: str
    WorkAddressID: str
    WorkPhone: str
    Active: bool
    WorkReleaseNotificationPreference: int
    OverrideRequirements: int

    @property
    def ParentID(self):
        return None

    @property
    def JobDescription(self):
        return None

    @property
    def WorkMobile(self):
        return None

    @property
    def IsPrimaryContact(self):
        return None

    @property
    def IsSecondaryContact(self):
        return None

    @property
    def WorkEmail(self):
        return None

    @property
    def PersonalPhone(self):
        return None

    @property
    def PersonalMobile(self):
        return None

    @property
    def PersonalEmail(self):
        return None

    @property
    def FirstName(self):
        return None

    @property
    def MiddleNames(self):
        return None

    @property
    def LastName(self):
        return None

    @property
    def HavertonContactType(self):
        return 'service_provider'
