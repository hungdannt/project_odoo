# -*- coding: utf-8 -*-

from odoo.tests.common import tagged
from odoo.fields import Command
from odoo.addons.zet_sale_management.tests.test_onchange_price_or_foreign_price import TestPriceOrForeiginPrice


@tagged('post_install', '-at_install')
class TestSaleOrder(TestPriceOrForeiginPrice):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()
        cls.pricelist2 = cls.env['product.pricelist'].create({
            'name': 'Test Pricate 2',
            'currency_id': cls.env.ref('base.USD').id,
            'foreign_currency_id': cls.env.ref('base.HKD').id,
            'item_ids': [Command.create({
                'product_tmpl_id': cls.product.id,
                'fixed_price': 200.00,
                'foreign_price': 25.00,
                'conversion_rate': 8.00,
            })],
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Wintermute',
            'city': 'Charleroi',
            'country_id': cls.env.ref('base.be').id,
            'peppol_eas': '0208',
            'peppol_endpoint': '3141592654',
        })
        cls.pricelist3 = cls.env['product.pricelist'].create({
            'name': 'Test Pricate 3',
            'currency_id': cls.env.ref('base.USD').id,
            'foreign_currency_id': cls.env.ref('base.HKD').id,
            'item_ids': [Command.create({
                'product_tmpl_id': cls.product.id,
                'fixed_price': 200.00,
                'foreign_price': 25.00,
                'conversion_rate': 8.00,
            }),
            Command.create({
                'product_tmpl_id': cls.product.id,
                'fixed_price': 700.00,
                'foreign_price': 100.00,    
                'conversion_rate': 7.00,
            })],
        })

    def test_action_update_prices(self):
        sale_order = self.env['sale.order'].create({
            'pricelist_id': self.pricelist2.id,
            'partner_id': self.partner.id,
            'order_line': [Command.create({
                'product_template_id': self.product.id,
                'product_id': self.product.product_variant_id.id,
                'foreign_price': 25.00,
                'fixed_price': 200.00,
                'conversion_rate': 8.00
            })]
        })
        sale_order.pricelist_id = self.pricelist
        sale_order.action_update_prices()
        self.assertEqual(sale_order.order_line.foreign_price, 12.90)
        self.assertEqual(sale_order.order_line.fixed_price, 100.00)
        self.assertEqual(sale_order.order_line.conversion_rate, 7.7)
        
    def test_pricelist_item_update(self):
        sale_order = self.env['sale.order'].create({
            'pricelist_id': self.pricelist3.id,
            'partner_id': self.partner.id,
            'order_line': [Command.create({
                'product_template_id': self.product.id,
                'product_id': self.product.product_variant_id.id,
                'foreign_price': 22.22,
                'fixed_price': 200.00,
                'conversion_rate': 9.00
            })]
        })
        sale_order.action_update_prices()
        self.assertEqual(sale_order.order_line.foreign_price, sale_order.order_line.pricelist_item_id.foreign_price)
        self.assertEqual(sale_order.order_line.fixed_price, sale_order.order_line.pricelist_item_id.fixed_price)
        self.assertEqual(sale_order.order_line.conversion_rate, sale_order.order_line.pricelist_item_id.conversion_rate)
