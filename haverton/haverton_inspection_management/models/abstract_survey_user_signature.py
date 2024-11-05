import base64
import re

from odoo import fields, models


class AbstractSurveyUserSignature(models.AbstractModel):
    _name = 'abstract.survey.user.signature'
    _description = 'This abstract model defines the user signature info.'

    user_signature = fields.Text(string='User Signature')
    user_signature_raw = fields.Text(string='Previous User Signature')

    def get_base64_user_signature(self):
        return base64.b64encode(self.user_signature.encode()).decode()

    def get_style_user_signature(self):
        viewbox_pattern = re.compile(r'viewBox="([^"]*)"')
        match = viewbox_pattern.search(self.user_signature)
        if not match:
            return "width: 224px; height: 167px;"
        viewbox_value = match.group(1)
        viewbox_components = viewbox_value.split()
        try:
            width = int(viewbox_components[2])
            height = int(viewbox_components[3])
            return f"width: {width}px; height: {height}px;"
        except Exception:
            return "width: 224px; height: 167px;"
