from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import object_session
from sqlmodel import Boolean, Column, Field, String

from .common import SQLModel
from .person_client_relationship import PersonClientRelationship
from .person_service_provider_relationship import PersonServiceProviderRelationship


class Person(SQLModel, table=True):
    ServiceProviderID: Optional[str] = Field(sa_column=Column(
        "PersonID", String, default=None, primary_key=True))
    FirstName: str
    MiddleNames: str
    LastName: str
    WorkUrl: str
    WorkAddressID: str
    WorkPhone: str
    WorkMobile: str
    WorkEmail: str
    PersonalPhone: str
    PersonalMobile: str
    PersonalEmail: str
    JobDescription: str
    Active: Optional[str] = Field(sa_column=Column("IsActive", Boolean))

    @property
    def ParentID(self):
        parent_id = object_session(self).scalar(
            select(PersonServiceProviderRelationship.ServiceProviderID).where(
                PersonServiceProviderRelationship.PersonID == self.ServiceProviderID)
        )
        if parent_id is None:
            parent_id = object_session(self).scalar(
                select(PersonClientRelationship.ClientID).where(
                    PersonClientRelationship.PersonID == self.ServiceProviderID)
            )
        return parent_id

    @property
    def IsPrimaryContact(self):
        is_primary_contact = object_session(self).scalar(
            select(PersonServiceProviderRelationship.IsPrimaryContact).where(
                PersonServiceProviderRelationship.PersonID == self.ServiceProviderID)
        )
        if is_primary_contact is None:
            is_primary_contact = object_session(self).scalar(
                select(PersonClientRelationship.IsPrimaryContact).where(
                    PersonClientRelationship.PersonID == self.ServiceProviderID)
            )
        return is_primary_contact

    @property
    def IsSecondaryContact(self):
        return object_session(self).scalar(
            select(PersonClientRelationship.IsSecondaryContact).where(
                PersonClientRelationship.PersonID == self.ServiceProviderID)
        )

    @property
    def OrganisationName(self):
        return ("%s %s %s" % (self.FirstName or '', self.MiddleNames or '', self.LastName or '')).strip()

    @property
    def OrganisationTradingAsName(self):
        return self.OrganisationName

    @property
    def WorkReleaseNotificationPreference(self):
        return None

    @property
    def EntityCode(self):
        return None

    @property
    def ABN(self):
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
        return 'person'
