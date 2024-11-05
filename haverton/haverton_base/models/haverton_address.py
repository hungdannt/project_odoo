# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HavertonAddress(models.Model):
    _name = 'haverton.address'
    _description = 'Haverton Address'
    _inherit = 'abstract.uuid'

    name = fields.Char(string='Single Line Address', compute='_compute_name', store=True)
    site_address = fields.Text(compute='_compute_site_address', store=True)
    subject_mail_address = fields.Text(compute='_compute_subject_mail_address')
    address_1 = fields.Char()
    address_2 = fields.Char()
    suburb = fields.Char()
    state = fields.Char()
    postcode = fields.Char()
    country = fields.Char()
    lot_number = fields.Char()
    dp_lot_number = fields.Char()
    block_number = fields.Char()
    section_number = fields.Char()
    po_box_number = fields.Char()
    property_name = fields.Char()
    map_friendly_address = fields.Char()

    @api.depends('lot_number', 'address_1', 'address_2', 'po_box_number', 'suburb', 'state', 'postcode', 'property_name')
    def _compute_name(self):
        for rec in self:
            lot = ('Lot ' + rec.lot_number) if rec.lot_number else None
            street_elements = [rec.address_1,
                               rec.address_2, rec.po_box_number]
            street = ' '.join(filter(None, street_elements)
                              ) if any(street_elements) else None
            capital_elements = [rec.suburb,
                                rec.state, rec.postcode]
            capital = ' '.join(filter(None, capital_elements)) if any(
                capital_elements) else None
            rec.name = ', '.join(
                filter(None, [lot, rec.property_name, street, capital]))

    @api.depends('lot_number', 'address_1', 'address_2', 'po_box_number', 'suburb', 'state', 'postcode', 'property_name')
    def _compute_site_address(self):
        for rec in self:
            line_1 = rec.property_name
            lot = ('Lot ' + rec.lot_number) if rec.lot_number else None
            street_elements = [rec.address_1,
                               rec.address_2, rec.po_box_number]
            street = ', '.join(filter(None, street_elements)
                               ) if any(street_elements) else None
            line_2 = ', '.join(filter(None, [lot, street]))
            line_3 = ' '.join(
                filter(None, [rec.suburb, rec.state, rec.postcode]))
            rec.site_address = '\n'.join(
                filter(None, [line_1, line_2, line_3]))

    @api.depends('lot_number', 'address_1', 'suburb', 'state', 'postcode')
    def _compute_subject_mail_address(self):
        for rec in self:
            rec.subject_mail_address =  f"{'Lot ' + rec.lot_number + ', ' if rec.lot_number else ''}" \
                                        f"{rec.address_1 + ', ' if rec.address_1 else ''}" \
                                        f"{rec.suburb + ', ' if rec.suburb else ''}" \
                                        f"{rec.state + ', ' if rec.state else ''}" \
                                        f"{rec.postcode}".rstrip(", ")
