from odoo import fields, models

from ..tools.text import get_html_plain_text


class MailMessage(models.Model):
    _name = 'mail.message'
    _inherit = ['abstract.uuid', 'mail.message']

    is_companion_message = fields.Boolean()
    haverton_message_type = fields.Char()
    user_ids = fields.Many2many('res.users', string="Recipient Users")

    def _auto_init(self):
        super()._auto_init()
        # set subtype = note for all messages synchronized from the Companion system
        note_subtype = self.env.ref('mail.mt_note')
        if note_subtype:
            self.search([('haverton_uuid', '!=', False), ('subtype_id', '=', False)]).write({
                'subtype_id': note_subtype.id
            })

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec.assign_message_recipients(
                partner_ids=vals.get('partner_ids'),
                user_ids=vals.get('user_ids'),
            )
        return res

    def assign_message_recipients(self, partner_ids: list[int] | None, user_ids: list[int] | None):
        self.ensure_one()
        if any([
            partner_ids and user_ids,
            not partner_ids and not user_ids,
        ]):
            return

        if partner_ids:
            # extract user_ids from partner_ids
            new_user_ids = self.env['res.users'].search(
                [('partner_id', 'in', partner_ids)]).ids
            if new_user_ids and set(new_user_ids) != set(self.user_ids.ids):
                self.user_ids = new_user_ids
        else:
            # extract partner_ids from user_ids
            new_partner_ids = self.env['res.users'].browse(
                user_ids).mapped('partner_id.id')
            if new_partner_ids and set(new_partner_ids) != set(self.partner_ids.ids):
                self.partner_ids = new_partner_ids

    def _assign_fields_after_creation(self):
        super()._assign_fields_after_creation()
        partner_ids = self.partner_ids
        user_ids = self.user_ids
        self.assign_message_recipients(
            partner_ids=partner_ids.ids, user_ids=user_ids.ids)

    def get_body_plain_text(self):
        self.ensure_one()
        return get_html_plain_text(self.body or '')
