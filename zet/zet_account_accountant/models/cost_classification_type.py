from odoo import models, fields


class CostClassificationType(models.Model):
    _name = "cost.classification.type"

    name = fields.Char()
