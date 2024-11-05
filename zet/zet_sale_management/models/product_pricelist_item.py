from odoo import _, api, fields, models
from odoo.osv import expression

class ProductPricelistItem(models.Model):
    _name = 'product.pricelist.item'
    _inherit = ['product.pricelist.item', 'foreign.amount']
    _order = 'sequence, id desc'

    foreign_currency_id = fields.Many2one(
        comodel_name='res.currency',
        help="The optional other currency if it is a multi-currency entry.",
        related='pricelist_id.foreign_currency_id'
    )
    sequence = fields.Integer()
    product_template_ids = fields.Many2many('product.template', compute="_compute_product_template_ids")

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        """
        On change of product_tmpl_id, update categ_id with the category 
        of the selected product template if categ_id is not already set.
        """
        for rec in self:
            if not rec.categ_id:
                rec.categ_id = rec.product_tmpl_id.categ_id

    @api.depends('categ_id')
    def _compute_product_template_ids(self):
        for rec in self:
            domain = ['|', ('company_id', '=', rec.company_id.id), ('company_id', '=', False)]
            if rec.categ_id:
                domain = expression.AND([
                    domain,
                    ['|', ('categ_id', '=', rec.categ_id.id), ('categ_id', '=', False)]])
            rec.product_template_ids = rec.product_template_ids.search(domain)
