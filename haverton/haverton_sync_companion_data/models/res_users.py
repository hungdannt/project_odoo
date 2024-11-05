import contextlib
import logging
import re

from odoo import Command, _, api, models
from odoo.addons.auth_signup.models.res_partner import now
from odoo.exceptions import UserError

from ..companion.models import User

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = ['res.users', 'abstract.companion.data.sync']

    @property
    def companion_model(self):
        return User

    @property
    def companion_primary_column_name(self):
        return 'UserID'

    def _action_reset_password_in_data_sync(self):
        if self.env.context.get('install_mode') or self.env.context.get('import_file'):
            return
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(
            signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        account_created_template = None
        if create_mode:
            account_created_template = self.env.ref(
                'auth_signup.set_password_email', raise_if_not_found=False)
            if account_created_template and account_created_template._name != 'mail.template':
                _logger.error("Wrong set password template %r",
                              account_created_template)
                return

        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'message_type': 'user_notification',
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }

        for user in self:
            if not user.active:
                continue
            if not user.email:
                raise UserError(
                    _("Cannot send email: user %s has no email address.", user.name))
            email_values['email_to'] = user.email
            with contextlib.closing(self.env.cr.savepoint()):
                if account_created_template:
                    account_created_template.send_mail(
                        user.id, force_send=True,
                        raise_exception=True, email_values=email_values)
                else:
                    body = self.env['mail.render.mixin']._render_template(
                        self.env.ref('auth_signup.reset_password_email'),
                        model='res.users', res_ids=user.ids,
                        engine='qweb_view', options={'post_process': True})[user.id]
                    mail = self.env['mail.mail'].sudo().create({
                        'subject': _('Password reset'),
                        'email_from': user.company_id.email_formatted or user.email_formatted,
                        'body_html': body,
                        **email_values,
                    })
                    mail.send()
            _logger.info(
                "Password reset email sent for user <%s> to <%s>", user.login, user.email)

    def _action_reset_password(self):
        """
        Overwrite the _action_reset_password function of Odoo base.
        If in_data_sync is True, allow create the inactive user.
        """
        if self.env.context.get('in_data_sync'):
            return self._action_reset_password_in_data_sync()
        return super()._action_reset_password()

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'WorkDirect': 'work_direct',
            'WorkEmail': 'login',
            'LogonName': 'haverton_logon_name',
            'WorkPhone': 'phone',
            'JobDescription': 'function',
            'IsActive': 'haverton_active',
            'IsSupervisor': 'is_supervisor',
            'FirstName': 'haverton_first_name',
            'MiddleNames': 'haverton_middle_name',
            'LastName': 'haverton_last_name'
        }

    def prepare_login(self, value):
        haverton_logon_name = value.get('haverton_logon_name') or ''
        mail_domain = self.get_haverton_mail_domain()
        return re.sub("\s\s*", ".", haverton_logon_name.strip()).lower() + mail_domain

    @api.model
    def prepare_companion_values(self, list_values, sql_session):
        res = super(ResUsers, self).prepare_companion_values(
            list_values,  sql_session)
        for value in res:
            if not value.get('login'):
                value['login'] = self.prepare_login(value)
            value['email'] = value['login']
            if self.env.context.get('is_create', False):
                value['name'] = '{}{}{}'.format(
                    value['haverton_first_name'] +
                    ' ' if value.get('haverton_first_name') else '',
                    value['haverton_middle_name'] +
                    ' ' if value.get('haverton_middle_name') else '',
                    value['haverton_last_name'] or ''
                ) or value.get('haverton_logon_name', '')
            if value.get('is_supervisor', False):
                site_supervisor_group = self.env.ref(
                    'haverton_base.haverton_base_group_site_supervisor')
                if site_supervisor_group:
                    value['groups_id'] = [
                        Command.link(site_supervisor_group.id)]
        return res
