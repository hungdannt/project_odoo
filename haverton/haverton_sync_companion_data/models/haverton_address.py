from odoo import api, models
import json

from ..companion.models import Address


class HavertonAddress(models.Model):
    _name = 'haverton.address'
    _inherit = ['abstract.companion.data.sync', 'haverton.address']

    @property
    def companion_model(self):
        return Address

    @property
    def companion_primary_column_name(self):
        return 'AddressID'

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'Address1': 'address_1',
            'Address2': 'address_2',
            'Suburb': 'suburb',
            'State': 'state',
            'Postcode': 'postcode',
            'Country': 'country',
            'LotNumber': 'lot_number',
            'DpLotNumber': 'dp_lot_number',
            'BlockNumber': 'block_number',
            'SectionNumber': 'section_number',
            'PoBoxNumber': 'po_box_number',
            'PropertyName': 'property_name',
            'MapFriendlyAddress': 'map_friendly_address',
        }
