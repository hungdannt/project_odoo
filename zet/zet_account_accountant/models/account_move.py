from odoo import  models, fields, api, _
from markupsafe import Markup
from odoo.exceptions import UserError
from odoo.addons.zet_sale_management.models.sale_order import get_account_ids_from_lines

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    vessel_name = fields.Text()
    port = fields.Char()
    date_of_arrival = fields.Date(default=lambda x: fields.Date.today())
    date_of_departure = fields.Date(default=lambda x: fields.Date.today())
    hide_exchange_price = fields.Boolean(compute='_compute_hide_exchange_price')
    foreign_currency_id = fields.Many2one('res.currency')
    classification_type_id = fields.Many2one('cost.classification.type', string="Type")
    invoice_ref_date = fields.Date(string='Invoice Reference Date')
    vsl_completion_date = fields.Date(string="VSL Completion Date")
    bank_transfers_date = fields.Date()
    remarks = fields.Text()
    inv_amount = fields.Monetary(string='Invoice Amount', compute='_compute_inv_amount')
    credit_amount = fields.Monetary(string='Credit Amount', compute='_compute_credit_amount')
    net_amount = fields.Monetary(string='Net Amount', compute='_compute_net_amount')
    job_number_ids = fields.Many2many('sale.order', compute='_compute_job_number_ids')
    job_number_text = fields.Text(compute='_compute_job_number_text', string="Job Number")
    invoice_ref = fields.Text(string='Invoice Reference Number')
    paid_amount = fields.Monetary(compute='_compute_paid_amount')
    paid_date = fields.Date(compute='_compute_paid_amount')
    down_payment_amount = fields.Monetary(compute='_compute_downpayment_amount')
    down_payment_date = fields.Date(compute='_compute_downpayment_amount')
    fund_collection_days = fields.Date()
    settlement_amount = fields.Monetary(compute='_compute_income_amount')
    settlement_date = fields.Date(compute='_compute_income_amount')
    bank_charges_dp = fields.Monetary(compute='_compute_downpayment_amount')
    bank_charges_settlement = fields.Monetary(compute='_compute_income_amount')
    balance_amount = fields.Monetary(compute='_compute_balance')
    is_downpayment = fields.Boolean(compute='_compute_is_downpayment', store=True)
    exchange_rate = fields.Float(compute='_compute_exchange_rate')
    show_waring_convert_rate = fields.Boolean(compute="_compute_show_waring_convert_rate")
    show_waring_exchange_rate = fields.Boolean(compute="_compute_show_waring_exchange_rate")
    text_waring_exchange_rate = fields.Html(compute="_compute_show_waring_exchange_rate")
    paid_by = fields.Text(compute='_compute_paid_by')
    
    @api.depends('invoice_line_ids.conversion_rate', 'invoice_date', 'foreign_currency_id')
    def _compute_show_waring_exchange_rate(self):
        for rec in self:
            rec.show_waring_exchange_rate = False
            rec.text_waring_exchange_rate = False
            if rec.foreign_currency_id == rec.company_id.currency_id and rec.invoice_line_ids and rec.foreign_currency_id  != rec.currency_id:
                rates = [item['conversion_rate'] for item in rec.invoice_line_ids if  item.display_type=='product' ]
                system_rate = rec.currency_id.round(rec.with_context(date=rec.invoice_date).currency_id.rate)
                rates = [x for x in rates if x != system_rate]
                rec.show_waring_exchange_rate = len(rates) >= 1
                rec.text_waring_exchange_rate = Markup(
                    _("Alert: A mismatch has been found between the user-defined exchange rate for some invoice items (%s) and the system's rate (%s) in 'Accounting > Configuration > Currencies'. This could lead to an discrepancy between Invoice and Journal amounts.<br/>Ensure all data is correct. For exchange rate changes, contact your Accounting Admin or IT team.", ', '.join(map(str, rates)), system_rate))


    @api.depends('invoice_line_ids.conversion_rate')
    def _compute_show_waring_convert_rate(self):
        for rec in self:
            # Extract the 'rate' values from the dictionaries
            rates = [item['conversion_rate'] for item in rec.invoice_line_ids if  item.display_type=='product' ]
            # Check if all 'rate' values are different
            rec.show_waring_convert_rate = len(set(rates)) not in [0, 1]

    @api.depends('currency_id', 'foreign_currency_id')
    def _compute_hide_exchange_price(self):
        for rec in self:
            rec.hide_exchange_price = rec.currency_id == rec.foreign_currency_id or not rec.foreign_currency_id

    def get_lable_amount(self, currency_id):
        return _("Amount (%s)", currency_id.name)

    @api.model
    def retrieve_dashboard(self, domain=[]):
        currency = self.get_currency_active()
        expenseAtm, paid, unpaid = self.get_total_expense_atm(currency, domain)
        currency_name = currency.mapped('name')
        name_total = _("Total amount in %s", self.env.company.currency_id.name)
        currency_name.append(name_total)
        return  {
                 'currency': currency_name,
                 'data': {
                    'expenseAtm' :  {
                        'name': _('Expense Amount') if self._context.get('cost_report') else _('Invoice Amount'),
                        'data': expenseAtm
                    },
                     'paid' :  {
                        'name': _('Paid'),
                        'data': paid
                     },
                     'unpaid' : {
                        'name': _('Unpaid'),
                        'data': unpaid
                     },
                }
             }

    def get_currency_active(self):
        return self.env['res.currency'].search([])
    
    def get_total_expense_atm(self, currency_ids, domain=[]):
        account_ids = self.search(domain)
        expenseAtm, unpaid, paid = [], [], []

        for currency in currency_ids:
            currency_id = currency.id
            currency_format = currency.round

            if self._context.get('cost_report'):
                total = sum(account_ids.filtered(lambda x: x.currency_id.id == currency_id).mapped('amount_total'))
            else:
                total = sum(account_ids.filtered(lambda x: x.currency_id.id == currency_id).mapped('amount_total_in_currency_signed'))

            total_unpaid = sum(account_ids.filtered(lambda x: x.currency_id.id == currency_id).mapped('amount_residual'))

            paid.append("{:.2f}".format(currency_format(total - total_unpaid)))
            expenseAtm.append("{:.2f}".format(currency_format(total)))
            unpaid.append("{:.2f}".format(currency_format(total_unpaid)))

        currency = self.env.company.currency_id
        currency_format = currency.round

        if self._context.get('cost_report'):
            total_amount_total_signed = sum([-x for x in account_ids.mapped('amount_total_signed')])
            total_amount_residual = sum([-x for x in account_ids.mapped('amount_residual_signed')])
        else:
            total_amount_total_signed = sum(account_ids.mapped('amount_total_signed'))
            total_amount_residual = sum(account_ids.mapped('amount_residual_signed'))
        
        expenseAtm.append("{:.2f}".format(currency_format(total_amount_total_signed)))
        unpaid.append("{:.2f}".format(currency_format(total_amount_residual)))
        paid.append("{:.2f}".format(currency_format(total_amount_total_signed - total_amount_residual)))

        return expenseAtm, paid, unpaid


    @api.depends('reversal_move_id.amount_total')
    def _compute_credit_amount(self):
        for rec in self:
            rec.credit_amount = sum(rec.reversal_move_id.mapped('amount_total'))
            
    @api.depends('inv_amount', 'credit_amount')
    def _compute_net_amount(self):
        for rec in self:
            rec.net_amount = rec.inv_amount - rec.credit_amount
            
    @api.depends('invoice_line_ids.job_number_ids')
    def _compute_job_number_ids(self):
        for rec in self:
            rec.job_number_ids = rec.invoice_line_ids.job_number_ids
    
    @api.depends('line_ids.amount_residual')
    def _compute_paid_amount(self):
        for rec in self:
            reconciled_partials = rec.sudo()._get_all_reconciled_invoice_partials()
            rec.paid_amount = sum(item['amount'] for item in reconciled_partials) if reconciled_partials else 0
            rec.paid_date = max(item['aml'].date for item in reconciled_partials) if reconciled_partials else None

    @api.depends('job_number_ids')
    def _compute_job_number_text(self):
        for rec in self:
            rec.job_number_text = '\n'.join(rec.job_number_ids.mapped('name'))

    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_income_amount(self):
        for rec in self:
            reconciled_partials = rec.sudo()._get_all_reconciled_invoice_partials()
            payment_ids = [item['aml'].payment_id for item in reconciled_partials] if reconciled_partials else None
            if payment_ids:
                rec.settlement_amount = sum(payment.amount for payment in payment_ids)
                dates = [(payment.date, payment) for payment in payment_ids if payment.date]
                if dates: 
                    latest_date, latest_payment = max(dates, key=lambda x: x[0])
                    rec.settlement_date = latest_date
                    rec.paid_by = latest_payment.paid_by
                dates = [payment.date for payment in payment_ids if payment.date]
                rec.settlement_date = max(dates) if dates else None
                rec.bank_charges_settlement = sum(payment.bank_charges for payment in payment_ids) 
            else:
                rec.settlement_amount = 0
                rec.settlement_date = None
                rec.bank_charges_settlement = 0

    @api.depends('move_type', 'line_ids.amount_residual', 'line_ids.sale_line_ids.order_id.invoice_ids')
    def _compute_downpayment_amount(self):
        for rec in self:
                move_ids = rec.line_ids.sale_line_ids.order_id.invoice_ids.filtered(lambda x: x.is_downpayment)
                bank_charges_dp = 0
                down_payment_amount = 0
                dates = []
                for move in move_ids:
                    reconciled_partials = move.sudo()._get_all_reconciled_invoice_partials()
                    payment_ids = [item['aml'].payment_id for item in reconciled_partials] if reconciled_partials else None
                    if payment_ids:
                        down_payment_amount += sum(payment.amount for payment in payment_ids) 
                        dates.append(max((payment.date for payment in payment_ids if payment.date), default=None))
                        bank_charges_dp += sum(payment.bank_charges for payment in payment_ids) 
                    
                rec.down_payment_amount = down_payment_amount
                rec.down_payment_date = max((date for date in dates if date is not None), default=None)
                rec.bank_charges_dp = bank_charges_dp
    
    @api.depends('line_ids.sale_line_ids.is_downpayment')
    def _compute_is_downpayment(self):
        for rec in self:
            rec.is_downpayment = rec._is_downpayment()

    @api.depends('net_amount', 'down_payment_amount', 'settlement_amount', 'bank_charges_settlement')
    def _compute_balance(self):
        for rec in self:
            rec.balance_amount = rec.net_amount - rec.down_payment_amount \
               - rec.bank_charges_dp - rec.settlement_amount - rec.bank_charges_settlement

    @api.depends('currency_id', 'invoice_date')
    def _compute_exchange_rate(self):
        for rec in self:
            rec.exchange_rate =rec.currency_id.round(rec.with_context(date=rec.invoice_date).currency_id.rate)

    @api.depends('amount_total', 'line_ids')
    def _compute_inv_amount(self):
        for rec in self:
            downpayment_lines = rec.line_ids._get_downpayment_lines()
            rec.inv_amount = rec.amount_total - sum(downpayment_lines.mapped('amount_currency'))
    
    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_paid_by(self):
        for rec in self:
            rec.paid_by = None
            if rec.move_type == 'in_invoice':
                reconciled_partials = rec.sudo()._get_all_reconciled_invoice_partials()
                if reconciled_partials:
                    payment_ids = [item['aml'].payment_id for item in reconciled_partials if item['aml'].payment_id]
                    if payment_ids:
                        latest_payment = max(payment_ids, key=lambda p: p.create_date)
                        rec.paid_by = latest_payment.paid_by
                    
    def action_register_payment(self):
        res = super().action_register_payment()
        context = res.setdefault('context', {})
        context['default_paid_by'] = self.paid_by
        return res
    
    def _get_quotation_template_value(self):
        return  {
            'name': self.partner_id.name,
            'partner_id': self.partner_id.id,
            'sale_order_template_line_ids': [(0, 0, {
                'sequence': line.sequence,
                'name': line.name,
                'product_id': line.product_id.id,
                'is_sub_section': line.is_sub_section,
                'display_type': line.display_type,
            }) for line in self.line_ids if line.display_type in ['line_section', 'line_note', False]],
            'note': self.narration
        }

    def action_convert_to_template(self):
        self.ensure_one()
        template = self.env['sale.order.template'].create(self._get_quotation_template_value())
        return {
            'name': _('Quotation Template'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.template',
            'view_mode': 'form',
            'res_id': template.id,
        }

    def action_analyze(self):
        self.ensure_one()
        set_account_ids = get_account_ids_from_lines(self.line_ids)
        if not set_account_ids:
            raise UserError(_('Please add valid analytic distribution in lines.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Analytic Account'),
            'view_mode': 'form',
            'res_model': 'select.analytic.wizard',
            'context': {
                        'default_analytic_account_ids': [(6, 0, list(set_account_ids))],
                    },
            'target': 'new',
        }
