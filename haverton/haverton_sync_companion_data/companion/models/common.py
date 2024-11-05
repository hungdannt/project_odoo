from typing import Any

from sqlmodel import SQLModel as OriginSQLModel


class SQLModel(OriginSQLModel):
    @property
    def fields_not_sync(self):
        """
        Returns fields can not be used when query Companion data to sync
        """
        return []

    def __init__(self, *args: Any, **kwargs: Any):
        if not kwargs:
            # Get a "list" of field names (or key view)
            field_names = [field for field in self.model_fields.keys(
            ) if field not in self.fields_not_sync]
            # Combine the field names and args to a dict using the positions.
            kwargs = dict(zip(field_names, args))
        super().__init__(**kwargs)


class CompanionRelationalModel:
    """
    Represent the relational table which mapping with the many2many field in Odoo
    """

    def __init__(self, model: SQLModel, self_primary: str, second_primary: str):
        self.model = model
        self.self_primary = self_primary
        self.second_primary = second_primary
