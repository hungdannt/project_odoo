from typing import Optional

from sqlmodel import Column, Field, String

from .common import SQLModel


class Client(SQLModel, table=True):
    ServiceProviderID: Optional[str] = Field(sa_column=Column(
        "ClientID", String, default=None, primary_key=True))
    OrganisationName: str
    OrganisationTradingAsName: str
    EntityCode: str
    ABN: str
    WorkUrl: str
    WorkAddressID: str
    WorkPhone: str
    WorkMobile: str
    WorkEmail: str

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
    def ParentID(self):
        return None

    @property
    def JobDescription(self):
        return None

    @property
    def IsPrimaryContact(self):
        return None

    @property
    def IsSecondaryContact(self):
        return None

    @property
    def Active(self):
        return True

    @property
    def WorkReleaseNotificationPreference(self):
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
    def OverrideRequirements(self):
        return None

    @property
    def HavertonContactType(self):
        return 'client'
