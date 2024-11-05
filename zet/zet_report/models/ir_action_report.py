import base64
import io

from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo import models



class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"


    def join_pdf(self, pdf_chunks):
        # Create empty pdf-writer object for adding all pages here
        result_pdf = PdfFileWriter()

        # Iterate for all pdf-bytes
        for chunk in pdf_chunks:
            # Read bytes
            chunk_pdf = PdfFileReader(
                stream=io.BytesIO(initial_bytes=chunk)  # Create steam object
            )
            # Add all pages to our result
            for page in range(chunk_pdf.getNumPages()):
                result_pdf.addPage(chunk_pdf.getPage(page))

        # Writes all bytes to bytes-stream
        response_bytes_stream = io.BytesIO()
        result_pdf.write(response_bytes_stream)
        return response_bytes_stream.getvalue()

    def _run_wkhtmltopdf(
        self,
        bodies,
        report_ref,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        res = super()._run_wkhtmltopdf(
            bodies,
            report_ref,
            header,
            footer,
            landscape,
            specific_paperformat_args,
            set_viewport_size,
        )
        report_sudo = self._get_report(report_ref)
        model_sudo = self.env[report_sudo.model].sudo()
        if 'attachment_pdf_ids' in model_sudo._fields:
            sale_order = model_sudo.browse(self._context.get('active_ids', []))
            for att in sale_order.attachment_pdf_ids:
                if att.mimetype == "application/pdf":
                    res = self.join_pdf([res, base64.b64decode(att.datas)])
        return res
