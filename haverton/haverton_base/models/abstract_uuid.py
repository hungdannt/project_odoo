from datetime import datetime
from uuid import uuid4

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import Query
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.sql import SQL


class AbstractUUID(models.AbstractModel):
    _name = 'abstract.uuid'
    _description = 'This abstract model defines the uuid for related models.'

    uuid = fields.Char(
        readonly=True,
        help='Alternate way to identify a record, used for access records from apis.',
        copy=False)

    _sql_constraints = [
        ("uuid_unique", "unique(uuid)", "The UUID must be unique."),
    ]
    haverton_uuid = fields.Char(copy=False)

    def _auto_init(self):
        super()._auto_init()
        # set uuid for the existing records
        try:
            if not self._abstract:
                self.env.cr.execute("""
                    UPDATE %s SET uuid=gen_random_uuid() WHERE id is not null and uuid is null
                """ % self._table)
        except Exception:
            self.env.cr.rollback()

    @property
    def haverton_updatable_fields(self):
        """
        Returns set of fields used for Haverton app and attributes of these fields can updated in the interface.
        Return: set()
        """
        return {}

    def browse_by_uuid(self, uuid: str):
        return self.search([('uuid', '=', uuid)], limit=1)

    def browse_by_uuids(self, uuids: list[str]):
        return self.search([('uuid', 'in', uuids)])

    def browse_by_haverton_uuid(self, uuid: str):
        if not uuid:
            return
        return self.sudo().with_context(active_test=False).search([('haverton_uuid', '=', uuid)], limit=1)

    def browse_by_haverton_uuids(self, uuids: list[str]):
        if not uuids:
            return []
        return self.sudo().with_context(active_test=False).search([('haverton_uuid', 'in', uuids)])

    def browse_by_primary_fields(self, **kwargs):
        """
        Overwrite this function in model containing multi the primary key
        """
        return

    def validate_by_uuid(self, uuid: str):
        rec = self.browse_by_uuid(uuid)
        if not rec:
            raise UserError(_("Record not found for %s.") % self._description)
        return rec

    def prepare_creation_vals_list(self, vals_list):
        for vals in vals_list:
            # add default value for uuid field
            vals['uuid'] = str(uuid4())
            for key, value in vals.items():
                if isinstance(value, datetime) and value:
                    vals[key] = value.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return vals_list

    def get_haverton_mail_domain(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'haverton_base.mail_domain'
        ) or '@havertonhomes.com.au'

    @api.model
    def prepare_haverton_values(self, values, is_update=False):
        updated_data = {}
        for key, value in values.items():
            if (is_update and value is None) or key not in self._fields:
                continue
            if isinstance(self._fields[key], fields.Datetime) and value:
                updated_data[key] = value.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
            elif isinstance(self._fields[key], fields.Many2one):
                relation_record = self[key].browse_by_uuid(value)
                updated_data[key] = relation_record.id if relation_record else False
            elif isinstance(self._fields[key], fields.Many2many):
                relation_records = self[key].browse_by_uuids(value)
                updated_data[key] = [Command.link(
                    rec.id) for rec in relation_records]
            # TODO: Handle other field types like One2many.
            else:
                updated_data[key] = value
        return updated_data

    def _order_field_to_sql(self, alias: str, field_name: str, direction: SQL,
                            nulls: SQL, query: Query) -> SQL:
        field = self._fields.get(field_name)
        if self.env.context.get('haverton_search') and field.type == 'char' and field.store and not field.translate:
            return SQL("%s %s %s", SQL(f'LOWER("{alias}"."{field_name}")'), direction, nulls)
        return super()._order_field_to_sql(alias, field_name, direction, nulls, query)

    def _assign_fields_after_creation(self):
        self.ensure_one()
        value_fields = self.get_assigned_value_fields()
        for field_name, new_value in value_fields.items():
            if field_name not in self._fields:
                continue
            field = self._fields[field_name]
            if any([
                isinstance(field, fields.Boolean),
                not isinstance(field, fields.Boolean) and not getattr(
                    self, field_name),
            ]):
                setattr(self, field_name, new_value)

    def get_assigned_value_fields(self):
        self.ensure_one()
        return {
            'haverton_create_date': self.create_date,
            'haverton_write_date': self.write_date,
        }

    def assign_fields_after_creation(self):
        for rec in self:
            rec._assign_fields_after_creation()

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = self.prepare_creation_vals_list(vals_list)
        res = super().create(vals_list)
        res.assign_fields_after_creation()
        return res
