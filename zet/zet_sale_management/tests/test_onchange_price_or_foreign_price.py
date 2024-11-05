# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged, Form
from odoo.fields import Command


@tagged('post_install', '-at_install')
class TestPriceOrForeiginPrice(TransactionCase):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()
        cls.product = cls.env['product.template'].create({
            'name': 'website_sale_cart_notification_product_1',
            'type': 'consu',
            'website_published': True,
            'list_price': 1000,
        })
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Test Pricate',
            'currency_id': cls.env.ref('base.USD').id,
            'foreign_currency_id': cls.env.ref('base.HKD').id,
            'item_ids': [Command.create({
                'product_tmpl_id': cls.product.id,
                'fixed_price': 100.00,
                'foreign_price': 12.90,
                'conversion_rate': 7.7,
            })],
        })

    def get_new_pricelist(self):
        pricelist = Form(self.env['product.pricelist'])
        pricelist.name = 'Test'
        pricelist.currency_id = self.env.ref('base.USD')
        pricelist.foreign_currency_id = self.env.ref('base.HKD')
        return pricelist

    def test_onchange_fixed_price(self):
        pricelist = self.get_new_pricelist()
        with pricelist.item_ids.new() as item:
            item.product_tmpl_id = self.product
            item.fixed_price = 200.00
            item.conversion_rate = 7.7
            self.assertEqual(item.foreign_price, round(200 / 7.7, 2))
            self.assertEqual(item.fixed_price, 200.00)
            self.assertEqual(item.conversion_rate, 7.7)

    def test_onchange_conversion_rate(self):
        pricelist = self.get_new_pricelist()
        with pricelist.item_ids.new() as item:
            item.product_tmpl_id = self.product
            item.fixed_price = 200.00
            item.conversion_rate = 7.0
            self.assertEqual(item.foreign_price, round(200 / 7.0, 2))
            self.assertEqual(item.fixed_price, 200.00)
            self.assertEqual(item.conversion_rate, 7.0)
            item.conversion_rate = 7.8
            self.assertEqual(item.foreign_price, round(200 / 7.8, 2))
            self.assertEqual(item.conversion_rate, 7.8)

    def test_onchange_foreign_price(self):
        pricelist = self.get_new_pricelist()
        with pricelist.item_ids.new() as item:
            item.product_tmpl_id = self.product
            item.fixed_price = 200.00
            item.conversion_rate = 7.0
            item.foreign_price = 100.00
            self.assertEqual(item.foreign_price, 100.00)
            self.assertEqual(item.fixed_price, 100.00 * 7.0)
            item.conversion_rate = 7.8
            self.assertEqual(item.foreign_price, round(100.00 * 7.0 / 7.8, 2))
            self.assertEqual(item.conversion_rate, 7.8)
