from odoo import api, models, fields, _


class Partner(models.Model):
    _inherit = "res.partner"

    person_in_charge = fields.Many2one('res.partner', string="Person In Charge")
    payment_term = fields.Date(string="Payment Term")

    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'JP')], limit=1)
        return country

    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_default_country)
    fax = fields.Char(string="FAX")

    @api.model
    def create(self, vals):
        jp_lang = self.env['res.lang'].sudo().search([('code', '=', 'ja_JP')])
        if 'lang' not in vals and jp_lang:
            vals['lang'] = 'ja_JP'
        res = super().create(vals)
        return res
