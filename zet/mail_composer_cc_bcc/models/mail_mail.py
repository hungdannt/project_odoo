import ast
import base64
import logging
import re
import smtplib

import psycopg2

from odoo import _, fields, models, tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)

def format_emails(partners):
    emails = [
        tools.formataddr((p.name or "False", p.email or "False")) for p in partners
    ]
    return ", ".join(emails)

class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None, alias_domain_id=False):
        env = self.env
        IrMailServer = env["ir.mail_server"]
        IrAttachment = env["ir.attachment"]
        ICP = env["ir.config_parameter"].sudo()
        is_out_of_scope = len(self.ids) > 1
        is_from_composer = self.env.context.get("is_from_composer", False)
        if is_out_of_scope or not is_from_composer:
            return super()._send(
                auto_commit=auto_commit,
                raise_exception=raise_exception,
                smtp_session=smtp_session,
            )
        mail = self
        success_pids = []
        failure_type = None
        try:
            if mail.state != "outgoing":
                if mail.state != "exception" and mail.auto_delete:
                    mail.sudo().unlink()
                return True

            body = mail.body_html or ""
            attachments = mail.attachment_ids
            for link in re.findall(r"/web/(?:content|image)/([0-9]+)", body):
                attachments = attachments - IrAttachment.browse(int(link))

            attachments = [
                (a["name"], base64.b64decode(a["datas"]), a["mimetype"])
                for a in attachments.sudo().read(["name", "datas", "mimetype"])
                if a["datas"] is not False
            ]

            # Instead of calling _send_prepare_values, directly format the emails here
            partner_to = [p for p in mail.recipient_ids if p not in mail.recipient_cc_ids + mail.recipient_bcc_ids]
            email_values = {
                "email_to": format_emails(partner_to),
                "email_cc": format_emails(mail.recipient_cc_ids),
                "email_bcc": format_emails(mail.recipient_bcc_ids),
                "email_from": mail.email_from,
                "subject": mail.subject,
                "body": mail.body_html,
            }

            headers = {}
            bounce_alias = ICP.get_param("mail.bounce.alias")
            catchall_domain = ICP.get_param("mail.catchall.domain")
            if bounce_alias and catchall_domain:
                headers["Return-Path"] = "%s@%s" % (bounce_alias, catchall_domain)
            if mail.headers:
                try:
                    headers.update(ast.literal_eval(mail.headers))
                except Exception as e:
                    _logger.warning("Error during update headers: %s" % e)

            mail.write({
                "state": "exception",
                "failure_reason": _(
                    "Error without exception. Probably due do sending an email without computed recipients."
                ),
            })

            notifs = self.env["mail.notification"].search(
                [
                    ("notification_type", "=", "email"),
                    ("mail_mail_id", "in", mail.ids),
                    ("notification_status", "not in", ("sent", "canceled")),
                ]
            )
            if notifs:
                notif_msg = _(
                    "Error without exception. Probably due do concurrent access update of notification records. Please see with an administrator."
                )
                notifs.sudo().write({
                    "notification_status": "exception",
                    "failure_type": "unknown",
                    "failure_reason": notif_msg,
                })
                notifs.flush_recordset(["notification_status", "failure_type", "failure_reason"])

            emails_from = tools.email_split_and_format(mail.email_from)
            email_from = emails_from[0] if emails_from else mail.email_from

            email_values["email_from"] = email_from
            msg = self.build_email(email_values, attachments=attachments, headers=headers)

            try:
                res = IrMailServer.send_email(
                    msg,
                    mail_server_id=mail.mail_server_id.id,
                    smtp_session=smtp_session,
                )
                success_pids += mail.recipient_ids.ids
            except AssertionError as error:
                if str(error) == IrMailServer.NO_VALID_RECIPIENT:
                    if not email_values.get("email_to") and failure_type != "mail_email_invalid":
                        failure_type = "mail_email_missing"
                    else:
                        failure_type = "mail_email_invalid"
                    _logger.info(
                        "Ignoring invalid recipients for mail.mail %s: %s",
                        mail.message_id,
                        email_values.get("email_to"),
                    )
                else:
                    raise
            if res:
                mail.write({"state": "sent", "message_id": res, "failure_reason": False})
                _logger.info(
                    "Mail with ID %r and Message-Id %r successfully sent",
                    mail.id,
                    mail.message_id,
                )
            mail._postprocess_sent_message(
                success_pids=success_pids, failure_type=failure_type
            )
        except MemoryError:
            _logger.exception(
                "MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option",
                mail.id,
                mail.message_id,
            )
            raise
        except (psycopg2.Error, smtplib.SMTPServerDisconnected):
            _logger.exception(
                "Exception while processing mail with ID %r and Msg-Id %r.",
                mail.id,
                mail.message_id,
            )
            raise
        except Exception as e:
            failure_reason = tools.ustr(e)
            _logger.exception(
                "failed sending mail (id: %s) due to %s", mail.id, failure_reason
            )
            mail.write({"state": "exception", "failure_reason": failure_reason})
            mail._postprocess_sent_message(
                success_pids=success_pids,
                failure_reason=failure_reason,
                failure_type="unknown",
            )
            if raise_exception:
                if isinstance(e, (AssertionError, UnicodeEncodeError)):
                    if isinstance(e, UnicodeEncodeError):
                        value = "Invalid text: %s" % e.object
                    else:
                        value = ". ".join(e.args)
                    raise MailDeliveryException(value) from e
                raise

        return True

    def build_email(self, email, attachments=None, headers=None):
        env = self.env
        mail = self
        email_from = email.get("email_from")
        IrMailServer = env["ir.mail_server"]
        msg = IrMailServer.build_email(
            email_from=email_from,
            email_to=email.get("email_to"),
            subject=mail.subject,
            body=email.get("body"),
            body_alternative=email.get("body_alternative"),
            email_cc=mail.email_cc,
            email_bcc=mail.email_bcc,
            reply_to=mail.reply_to,
            attachments=attachments,
            message_id=mail.message_id,
            references=mail.references,
            object_id=mail.res_id and ("%s-%s" % (mail.res_id, mail.model)),
            subtype="html",
            subtype_alternative="plain",
            headers=headers,
        )
        return msg
