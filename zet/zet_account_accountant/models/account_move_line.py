from odoo import  models, fields, api
from odoo.tools.float_utils import float_compare


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['account.move.line', 'upload.attach.file',  'foreign.amount']

    voucher_reference = fields.Char()
    is_sub_section = fields.Boolean()
    foreign_price_subtotal = fields.Monetary(
        compute='_foreign_price_subtotal_and_total',
        string="Amount (Foreign)",
        currency_field='foreign_currency_id',
    )
    fixed_price = fields.Float(
        related='price_unit', readonly=False, string="Price Unit (HKD)")
    foreign_price_total = fields.Monetary(
        compute='_foreign_price_subtotal_and_total',
        string="Foreign Tax incl.",
        currency_field='foreign_currency_id',
    )
    foreign_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Foreign Currency",
        help="The optional other currency if it is a multi-currency entry.",
        related="move_id.foreign_currency_id"
    )
    job_number_ids = fields.Many2many('sale.order', string="Job Number")
    price_unit = fields.Float(
        string='Unit Price',
        compute="_compute_price_unit", store=True, readonly=False, precompute=True,
        digits='Product Price',
        help="Price of products in Main currency"
    )
    
    @api.depends('quantity', 'discount', 'foreign_price', 'tax_ids', 'currency_id')
    def _foreign_price_subtotal_and_total(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False
            # Compute 'price_subtotal'.
            line_discount_price_unit = line.foreign_price * (1 - (line.discount / 100.0))
            subtotal = line.quantity * line_discount_price_unit

            # Compute 'price_total'.
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.foreign_currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.foreign_price_subtotal = taxes_res['total_excluded']
                line.foreign_price_total = taxes_res['total_included']
            else:
                line.foreign_price_total = line.foreign_price_subtotal = subtotal

    def _convert_to_tax_line_dict(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.
        :return: A python dictionary.
        """
        self.ensure_one()
        if self._context.get('foreign_tax_totals'):
            self.ensure_one()
            sign = -1 if self.move_id.is_inbound(include_receipts=True) else 1
            return self.env['account.tax']._convert_to_tax_line_dict(
                self,
                partner=self.partner_id,
                currency=self.currency_id,
                taxes=self.tax_ids,
                tax_tags=self.tax_tag_ids,
                tax_repartition_line=self.tax_repartition_line_id,
                group_tax=self.group_tax_id,
                account=self.account_id,
                analytic_distribution=self.analytic_distribution,
                tax_amount=sign * self.amount_currency,
            )
        return super()._convert_to_tax_line_dict()
    
    def _prepare_analytic_distribution_line(self, distribution, account_ids, distribution_on_each_plan):
        """ Overided to add the customer_id = partner_id to the analytic distributionline 
        """
        values = super()._prepare_analytic_distribution_line(distribution, account_ids, distribution_on_each_plan)
        for account in self.env['account.analytic.account'].browse(map(int, account_ids.split(","))).exists():
            values['customer_id'] = account.partner_id.id
        return values
