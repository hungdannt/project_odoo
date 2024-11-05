import json
from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.http import request

FORMAT_DATETIME = "%d, %B, %Y %H:%M:%S"
FORMAT_DATE = "%d, %B, %Y"
SALE_ORDER_STATE = [
    ('draft', "Draft"),
    ('sent', "Document Sent"),
    ('sale', "Confirmed"),
    ('cancel', "Cancelled"),
]

def get_account_ids_from_lines(lines):
    set_account_ids = set()
    for line in lines:
        if line.analytic_distribution:
            ids = [int(key) for key in line.analytic_distribution.keys()]
            set_account_ids.update(ids)
    return set_account_ids

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_fda = fields.Boolean()
    pda = fields.Many2one('sale.order', string="PDA")
    fda = fields.One2many('sale.order', 'pda', string="FDA")
    count_fda = fields.Integer(
        compute='_compute_count_fda')
    state = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    principal = fields.Char()
    purpose_of_call = fields.Char()
    customs_declaration_ref = fields.Char()
    postal_reference_sent_out_invoice = fields.Char(
        string="Postal Reference: Sent out Invoice")
    postal_reference_others = fields.Char(string='Postal Reference: Others')
    order_history_ids = fields.One2many('sale.order.history', "order_id")
    count_history = fields.Integer(compute="_compute_count_history")
    vessel_name = fields.Text()
    port = fields.Char()
    date_of_arrival = fields.Date(default=lambda x: fields.Date.today())
    date_of_departure = fields.Date(default=lambda x: fields.Date.today())
    total_file_size_in_line = fields.Integer(
        compute='_compute_total_file_size_in_line')
    foreign_currency_id = fields.Many2one('res.currency', related='pricelist_id.foreign_currency_id', readonly=False, store=True)
    hide_exchange_price = fields.Boolean(compute='_compute_hide_exchange_price')
    show_waring_convert_rate = fields.Boolean(compute="_compute_show_waring_convert_rate")
    price_list_ids = fields.Many2many('product.pricelist', related='partner_id.price_list_ids')
    conversion_rate = fields.Float(string="F(x) rate", default=0, digits=(16, 8))
    main_currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='currency_id',
        readonly=False,
        string="Main Currency",
        help="Input a main currency if user wants to select a new currency which is different from currency of Pricelist"
    )
    tmp_foreign_currency_id = fields.Many2one('res.currency', string="Foreign Currency",
        related='foreign_currency_id',
        help="Input a foreign currency if user wants to select a new currency which is different from foreign currency of Pricelist",
        readonly=False)
    rate = fields.Float(string="F(x) - Main currency", store=False, default=0, digits=(16,8))
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Determine the Main currency of PDA/FDA")

    def action_update_prices(self):
        super().action_update_prices()
        self.conversion_rate = self.pricelist_id.conversion_rate
        self.currency_id = self.pricelist_id.currency_id
        self.change_main_currency()


    @api.depends('order_line.conversion_rate')
    def _compute_show_waring_convert_rate(self):
        for rec in self:
            # Extract the 'rate' values from the dictionaries
            rates = [item['conversion_rate'] for item in rec.order_line if not item.display_type]
            # Check if all 'rate' values are different
            rec.show_waring_convert_rate = len(set(rates)) not in [0, 1]

    @api.depends('currency_id', 'foreign_currency_id')
    def _compute_hide_exchange_price(self):
        for rec in self:
            rec.hide_exchange_price = rec.currency_id == rec.foreign_currency_id or not rec.foreign_currency_id

    @api.onchange('partner_id')
    def _onchange_partner_set_template(self):
        if self.sale_order_template_id or not self.partner_id:
            return
        self.sale_order_template_id = self.sale_order_template_id.search(
            [('partner_id', '=', self.partner_id.id), ('set_as_default', '=', True)], limit=1)

    @api.onchange('order_line')
    def _onchange_order_line_create_note(self):
        sequence = 0
        for line in self.order_line:
            note = line.product_id.product_note
            sequence = line.sequence
            if self._check_auto_create_note(note):
                value = self._get_value_create_note(note, sequence)
                self.order_line = [(0, 0, value)]
            elif note:
                order_line = self.order_line.filtered(
                    lambda x: x.product_note == note)
                if order_line.sequence < line.sequence:
                    self.order_line = [
                        (1, line.id, {'sequence': order_line.sequence})]
                    self.order_line = [
                        (1, order_line.id, {'sequence': line.sequence + 1})]
                    line_update_sequence = self.order_line.filtered(
                        lambda x: x.sequence >= line.sequence + 1 and line.product_note != note)
                    if line_update_sequence:
                        for l in line_update_sequence:
                            self.order_line = [
                                (1, l.id, {'sequence': l.sequence + 1})]
        self.order_line.sorted('sequence')

    def _check_auto_create_note(self, note):
        return note and note not in self.order_line.mapped('product_note')

    def _get_value_create_note(self, note, sequence):
        return {
            'name': note.name,
            'order_id': self.id.origin,
            "product_note": note.id,
            'display_type': 'line_note',
            'sequence': sequence + 1
        }

    def _get_sequence_order_line(self, note):
        order_line = self.order_line.filtered_domain(
            [('product_note', '=', note.id)])
        if order_line:
            return order_line.sequence - 1
        return False

    @api.depends('order_line')
    def _compute_total_file_size_in_line(self):
        for rec in self:
            rec.total_file_size_in_line = sum(
                rec.order_line.attachment_ids.mapped('file_size'))

    @api.depends('order_history_ids')
    def _compute_count_history(self):
        for rec in self:
            rec.count_history = len(rec.order_history_ids)

    def write(self, value):
        if self.check_create_history(value):
            self.create_sale_order_history(value)
        return super().write(value)

    def check_create_history(self, value={}):
        list_field = ['name', 'date_order', 'vessel_name',
                      'port', 'date_of_arrival', 'date_of_departure', 'payment_term_id', 'order_line',
                      'tax_totals', 'signed_by', 'partner_id', 'amount_total']
        if not value:
            return False
        fields_edit = value.keys()
        for field in fields_edit:
            if field in list_field:
                return True
        return False

    def create_sale_order_history(self, value):
        self.order_history_ids.with_user(SUPERUSER_ID).create({
            'version_number': str(self.count_history + 1).zfill(3),
            'order_id': self.id,
            'name': self.name,
            'user_edit': self.env.uid,
            'old_value': self.get_old_value(),
            'signature': self.signature
        })

    def get_old_value(self, print_pdf=False):
        data = {
            'name': self.name,
            'date_order': self.date_order.strftime(FORMAT_DATETIME) if self.date_order else '',
            'vessel_name': self.vessel_name,
            'port': self.port,
            'date_of_arrival': self.date_of_arrival.strftime(FORMAT_DATE) if self.date_of_arrival else '',
            'date_of_departure': self.date_of_departure.strftime(FORMAT_DATE) if self.date_of_departure else '',
            'payment_term_id': self.payment_term_id.name,
            'order_line':  self.get_order_line(),
            'tax_totals': self.tax_totals,
            # 'signature': self.signature,
            'signed_by': self.signed_by,
            'parnter': self.partner_id.display_name,
            'amount_total': self.amount_total,
            'lable_amount': f'Amount ({self.currency_id.name})',
            'lable_foreign_amount': f'Amount ({self.foreign_currency_id.name})',
            'hide_exchange_price': self.hide_exchange_price,
            'address': {
                'street': self.partner_id.street,
                'street2': self.partner_id.street2,
                'city': self.partner_id.city,
                'state_id': self.partner_id.state_id.name,
                'country_id': self.partner_id.country_id.name,
            }
        }
        return json.dumps(data) if not print_pdf else data

    def get_order_line(self):
        line_ids = []
        for order_line in self.order_line:
            line = {
                'name': order_line.name,
                'display_type': order_line.display_type,
                'price_subtotal': order_line.price_subtotal,
                'is_downpayment': order_line.is_downpayment,
                'is_sub_section': order_line.is_sub_section,
                'product_uom_qty': order_line.product_uom_qty,
                'foreign_price_total':self.foreign_currency_id.format(order_line.foreign_price_total) if self.foreign_currency_id and order_line.foreign_price_total else ''
            }
            line_ids.append(line)
        return line_ids

    def action_view_history(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "sale.order.history",
            "domain": [('id', 'in', self.order_history_ids.ids)],
            "name": _("History"),
            'view_mode': 'tree'
        }
        return result

    def _get_name_portal_content_view(self):
        self.ensure_one()
        return 'zet_sale_management.sale_order_portal_content'

    def _has_to_be_signed(self):
        if request.params.get('history'):
            return False
        return super()._has_to_be_signed()

    def _has_to_be_paid(self):
        if request.params.get('history'):
            return False
        return super()._has_to_be_paid()

    def action_confirm(self):
        if self.is_fda:
            return super().action_confirm()
        else:
            self.write({
                'state': 'sale'
            })
    
    def update_value_create_fda(self):
        return {
            'currency_id': self.currency_id.id,
            'is_fda': True,
            'pda': self.id,
            'analytic_account_id': self.analytic_account_id.id
        }
            
    def create_fda(self):
        fda = self.copy(self.update_value_create_fda())
        return self._get_records_action_views(fda.name, fda.id)

    def action_view_fda(self):
        self.ensure_one()
        if len(self.fda) == 1:
            return self._get_records_action_views(self.fda[0].name, self.fda[0].id)
        elif len(self.fda):
            name = _('FDA')
            return self._get_records_action_views(name=name, view_mode='tree,form', domain=[('id', 'in', self.fda.ids)])

    def action_view_pda(self):
        return self._get_records_action_views(self.pda.name, self.pda.id)

    def _get_records_action_views(self, name, res_id=0, view_mode='form', domain=[]):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'view_mode': view_mode,
            'res_model': self._name,
            'res_id': res_id,
            'domain': domain
        }
    
    @api.depends('fda')
    def _compute_count_fda(self):
        for rec in self:
            rec.count_fda = len(rec.fda)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New") and vals.get('is_fda'):
                vals['name'] = self._get_name_fda(vals.get('date_order'))
        return super().create(vals_list)

    def _get_name_fda(self, date_order):
        seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(date_order)
                ) if date_order else None
        return  self.env['ir.sequence'].next_by_code(
                    'sale.order.fda', sequence_date=seq_date) or _("New")

    def get_lable_amount(self, currency_id):
        return _('Amount (%s)', currency_id.name)

    def _get_quotation_template_value(self):
        return {
            'name': self.partner_id.name,
            'partner_id': self.partner_id.id,
            'sale_order_template_line_ids': [(0, 0, {
                'sequence': line.sequence,
                'name': line.name,
                'product_id': line.product_id.id,
                'is_sub_section': line.is_sub_section,
                'display_type': line.display_type,
            }) for line in self.order_line if line.display_type in ['line_section', 'line_note', False]],
            'sale_order_template_option_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
            }) for line in self.sale_order_option_ids],
            'note': self.note
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

    def update_all_conversion_rate(self):
        for rec in self:
            rec.order_line.write({
                'conversion_rate': self._context.get('conversion_rate', 1)
            })
            rec.write({
                'foreign_currency_id': self._context.get('foreign_currency_id', rec.foreign_currency_id.id)
            })
            rec.order_line._onchange_fixed_price_or_conversion_rate()

    def change_main_currency(self):
        self.ensure_one()
        for line in self.order_line:
            line.price_unit = line.price_unit * self._context.get('rate', 1)
            line.fixed_price = line.price_unit
            line._onchange_fixed_price_or_conversion_rate()
        self.write({
            'currency_id': self._context.get('currency', self.currency_id.id)
        })

    @api.depends('pricelist_id', 'company_id')
    def _compute_currency_id(self):
        for order in self:
            order.currency_id = order._origin.currency_id or order.pda.currency_id or order.pricelist_id.currency_id or order.company_id.currency_id
        
    def action_select_analytic_wizard(self):
        self.ensure_one()
        set_account_ids = get_account_ids_from_lines(self.order_line)
        if self.analytic_account_id:
            set_account_ids.add(self.analytic_account_id.id)
        if not set_account_ids:
            raise UserError(_('Please set analytic account')) 
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
        
    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        for line in self.order_line:
            if not line.is_downpayment:
                invoiceable_line_ids.append(line.id)
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    down_payment_line_ids.append(line.id)
 
        return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)
