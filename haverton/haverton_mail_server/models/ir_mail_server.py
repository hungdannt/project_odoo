import base64
import logging
import uuid

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _name = 'ir.mail_server'
    _inherit = ['abstract.haverton.file', 'ir.mail_server']

    def write_eml_file(self, msg):
        if not self._context.get('save_attachment'):
            return
        eml_data = msg.as_string().encode('utf-8')
        base64_eml = base64.b64encode(eml_data)
        name = self._context.get('emg_file_name') or f"{uuid.uuid4()}.eml"
        res_model = self._context.get('res_model')
        res_id = self._context.get('res_id')
        folder_path = self.get_folder_path(res_model, res_id)
        attachment = self.create_eml_to_attachment(name, base64_eml, res_model)
        # save attachment to server
        file_path = self.write_data_to_file(folder_path, name, eml_data)
        attachment.url = file_path
        return attachment

    def create_eml_to_attachment(self, name, base64, res_model):
        return self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'datas': base64,
            'res_model': res_model,
        })

    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None,
                   smtp_ssl_certificate=None, smtp_ssl_private_key=None,
                   smtp_debug=False, smtp_session=None):
        res = super().send_email(message, mail_server_id, smtp_server, smtp_port, smtp_user,  smtp_password, smtp_encryption,
                                 smtp_ssl_certificate, smtp_ssl_private_key,
                                 smtp_debug, smtp_session)
        if res:
            self.write_eml_file(message)
        return res
