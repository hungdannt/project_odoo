import json

from odoo.http import  request


from odoo.addons.web.controllers.export import ExcelExport, ExportXlsxWriter

class ZetExportXlsxWriter(ExportXlsxWriter):
    def __init__(self, field_names, row_count=0, sumary=None):
        super().__init__(field_names, row_count)
        self.height_sumary = len(sumary.get('data')) + \
            3 if sumary.get('data') else 0
        self.sumary = sumary
        self.border_bold_style = self.workbook.add_format(
            {'text_wrap': True, 'bold': True, 'bg_color': '#e9ecef', 'border': True})

    def __enter__(self):
        self.write_sumary()
        return super().__enter__()

    def write_sumary(self):
        # Write currency headers
        for i, currency in enumerate(self.sumary.get('currency', [])):
            self.write(1, i + 2, currency, self.border_bold_style)
            self.write(1, 1, '', self.border_bold_style)

        # Write data
        data_summary = self.sumary.get('data', {})
        for i, key in enumerate(data_summary.keys()):
            self.write(i + 2, 1, data_summary[key]['name'],  self.border_bold_style)

            for index, price in enumerate(data_summary[key].get('data', [])):
                self.write(i + 2, index + 2, price, self.border_bold_style)

    def write_header(self):
        for i, fieldname in enumerate(self.field_names):
            self.write(self.height_sumary, i, fieldname, self.header_style)
        self.worksheet.set_column(
            0, max(0, len(self.field_names) - 1), 30)  # around 220 pixels


class ZetExcelExport(ExcelExport):

    def base(self, data):
        params = json.loads(data)
        self.model = None
        self.domain = []
        self.context = params.get('context', {})
        if params.get('context') and params['context'].get('get_summary_in_xlsx'):
            self.domain = params.get('domain', []) if not params.get(
                'ids') else [('id', 'in', params.get('ids'))]
            self.model = params.get('model')
        return super().base(data)

    def from_data(self, fields, rows):
        model = request.env[self.model] if self.model else None
        sumary = {}
        if hasattr(model, 'retrieve_dashboard'):
            sumary = model.with_context(self.context).retrieve_dashboard(self.domain)
        with ZetExportXlsxWriter(fields, len(rows), sumary) as xlsx_writer:
            for row_index, row in enumerate(rows):
                for cell_index, cell_value in enumerate(row):
                    xlsx_writer.write_cell(
                        row_index + xlsx_writer.height_sumary + 1, cell_index, cell_value)
        return xlsx_writer.value
