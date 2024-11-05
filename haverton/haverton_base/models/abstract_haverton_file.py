from pathlib import Path

from odoo import models


class AbstractHavertonFile(models.AbstractModel):
    _name = 'abstract.haverton.file'
    _description = 'This abstract model defines the info and methods of the Haverton file.'

    @property
    def job_directory_number_desired_width(self):
        return int(self.env['ir.config_parameter'].sudo().get_param(
            'haverton_base.job_directory_number_desired_width'
        ) or 5)

    @property
    def document_root_path(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'haverton_base.document_root_path'
        )

    def get_folder_path(self, res_model, res_id):
        folder_path = ''
        res = self.env[res_model].browse(res_id)
        if len(res) > 0:
            if res_model in ['project.task', 'survey.user_input']:
                if res.project_id:
                    folder_path = 'Docs/J%s/' % str(res.project_id.document_directory_number).zfill(
                        self.job_directory_number_desired_width)
        return folder_path

    def write_data_to_file(self, folder_path, fname, data):
        """
        Writes file to server.
            Return path of file
        """
        document_root_path = self.document_root_path
        if not document_root_path:
            return
        folder_path = document_root_path + folder_path
        path = folder_path + fname
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        f = open(path, 'wb')
        f.write(data)
        f.close()
        return path
