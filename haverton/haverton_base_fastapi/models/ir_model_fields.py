from odoo import _, fields, models
from odoo.exceptions import UserError
from psycopg2 import sql

Model = models.Model


class IrModelFields(Model):
    _inherit = 'ir.model.fields'

    show_on_mobile_profile = fields.Boolean(default=True)

    def write(self, vals):
        haverton_updatable_fields = self.env['ir.model.fields']
        base_fields = self.env['ir.model.fields']
        for item in self:
            if item.name in getattr(self.env[item.model], 'haverton_updatable_fields', []):
                haverton_updatable_fields += item
            else:
                base_fields += item
        haverton_res = True
        base_res = True
        if haverton_updatable_fields:
            haverton_res = haverton_updatable_fields.write_custom_fields(vals)
        if base_fields:
            base_res = super(IrModelFields, base_fields).write(vals)
        return haverton_res and base_res

    def write_custom_fields(self, vals):
        """
        Overwrite the write function of the ir.model.fields in base.
        Used to allow update the haverton fields in the interface.
        Remove logic: if item.state != 'manual' is raise error
        """
        if not self:
            return True

        # if set, *one* column can be renamed here
        column_rename = None

        # names of the models to patch
        patched_models = set()
        translate_only = all(
            self._fields[field_name].translate for field_name in vals)
        if vals and self and not translate_only:
            for item in self:
                if vals.get('model_id', item.model_id.id) != item.model_id.id:
                    raise UserError(
                        _("Changing the model of a field is forbidden!"))

                if vals.get('ttype', item.ttype) != item.ttype:
                    raise UserError(_("Changing the type of a field is not yet supported. "
                                      "Please drop it and create it again!"))

                obj = self.pool.get(item.model)
                field = getattr(obj, '_fields', {}).get(item.name)

                if vals.get('name', item.name) != item.name:
                    # We need to rename the field
                    item._prepare_update()
                    if item.ttype in ('one2many', 'many2many', 'binary'):
                        # those field names are not explicit in the database!
                        pass
                    else:
                        if column_rename:
                            raise UserError(
                                _('Can only rename one field at a time!'))
                        column_rename = (obj._table, item.name,
                                         vals['name'], item.index, item.store)

                # We don't check the 'state', because it might come from the context
                # (thus be set for multiple fields) and will be ignored anyway.
                if obj is not None and field is not None:
                    patched_models.add(obj._name)

        # These shall never be written (modified)
        for column_name in ('model_id', 'model', 'state'):
            if column_name in vals:
                del vals[column_name]

        res = super(Model, self).write(vals)

        self.env.flush_all()

        if column_rename:
            # rename column in database, and its corresponding index if present
            table, oldname, newname, index, stored = column_rename
            if stored:
                self._cr.execute(
                    sql.SQL('ALTER TABLE {} RENAME COLUMN {} TO {}').format(
                        sql.Identifier(table),
                        sql.Identifier(oldname),
                        sql.Identifier(newname)
                    ))
                if index:
                    self._cr.execute(
                        sql.SQL('ALTER INDEX {} RENAME TO {}').format(
                            sql.Identifier(f'{table}_{oldname}_index'),
                            sql.Identifier(f'{table}_{newname}_index'),
                        ))

        if column_rename or patched_models or translate_only:
            # setup models, this will reload all manual fields in registry
            self.env.flush_all()
            self.pool.setup_models(self._cr)

        if patched_models:
            # update the database schema of the models to patch
            models = self.pool.descendants(patched_models, '_inherits')
            self.pool.init_models(self._cr, models, dict(
                self._context, update_custom_fields=True))

        return res
