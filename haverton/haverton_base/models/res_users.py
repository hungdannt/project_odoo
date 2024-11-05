import logging
import re
import time

import odoo
from fastapi import HTTPException, status
from odoo import SUPERUSER_ID, Command, _, api, exceptions, fields, models, tools
from odoo.addons.auth_signup.models.res_partner import now
from odoo.exceptions import AccessDenied, UserError
from odoo.http import request
from odoo.modules.registry import Registry

from ..tools import jwt

_logger = logging.getLogger(__name__)

EMAIL_CONSTRAIN = '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PASSWORD_CONSTRAINS = ["^(?=(?:.*[A-Z]))(?=(?:.*[a-z]))(?=(?:.*[!@#$%^&*()]))([A-Za-z\d!@#$%^&*()]{8,20})$",
                       "^(?=(?:.*[A-Z]))(?=(?:.*[a-z]))(?=(?:.*\d))([A-Za-z\d!@#$%^&*()]{8,20})$",
                       "^(?=(?:.*[A-Z]))(?=(?:.*[!@#$%^&*()]))(?=(?:.*\d))([A-Za-z\d!@#$%^&*()]{8,20})$",
                       "^(?=(?:.*[a-z]))(?=(?:.*[!@#$%^&*()]))(?=(?:.*\d))([A-Za-z\d!@#$%^&*()]{8,20})$"]


class OauthSignupError(Exception):
    pass


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = ['res.users', 'abstract.uuid']

    uuid = fields.Char(
        readonly=True,
        required=True,
        help='Alternate way to identify a record, used for access records from apis.',
        copy=False)
    work_direct = fields.Char(help='The other phone number to contact.')
    main_haverton_menu_key = fields.Char(
        copy=False, help='The main menu item belong a user.')
    refresh_token_ids = fields.One2many(
        comodel_name='jwt.refresh.token',
        inverse_name='user_id',
    )
    is_supervisor = fields.Boolean()
    haverton_first_name = fields.Char()
    haverton_middle_name = fields.Char()
    haverton_last_name = fields.Char()
    haverton_logon_name = fields.Char()
    role = fields.Char(compute="_compute_role")
    haverton_active = fields.Boolean(default=True)
    function = fields.Char(string='Job Description')

    _sql_constraints = [
        ("uuid_unique", "unique(uuid)", "The UUID must be unique."),
    ]

    def _auto_init(self):
        super()._auto_init()
        # set uuid for the existing records
        self.env.cr.execute("""
            UPDATE res_users SET uuid=gen_random_uuid() WHERE id is not null and uuid is null
        """)

    @property
    def haverton_active_domain(self):
        return [
            ('active', '=', True),
            ('haverton_uuid', '!=', False),
            ('haverton_active', '=', True)
        ]

    @property
    def haverton_group_ids(self):
        category_haverton_role = self.env.ref(
            'haverton_base.module_category_haverton_role')
        return self.groups_id.filtered_domain([('category_id', '=', category_haverton_role.id)])

    @api.depends("groups_id")
    def _compute_role(self):
        for rec in self:
            rec.role = 'user'
            if self.env.ref('haverton_base.haverton_base_group_site_supervisor') in rec.groups_id:
                rec.role = "site_supervisor"
            if self.env.ref('haverton_base.haverton_base_group_admin') in rec.groups_id:
                rec.role = "admin"

    @api.constrains('login')
    def _check_login(self):
        for rec in self:
            if not re.fullmatch(EMAIL_CONSTRAIN, rec.login):
                raise exceptions.UserError(_('Login email is invalid.'))

    @api.constrains('main_haverton_menu_key')
    def _check_main_haverton_menu_key(self):
        for rec in self:
            if rec.main_haverton_menu_key and not self.env['ir.ui.menu'].search_count([('haverton_menu_key', '=', rec.main_haverton_menu_key)]):
                raise exceptions.UserError(
                    _('The main_haverton_menu_key is invalid.'))

    def reset_password(self, login):
        users = self.search(self._get_login_domain(login))
        if not users:
            users = self.search(self._get_email_domain(login))
        if not users:
            raise exceptions.UserError(
                _('Invalid email address. Please check and try again'))
        return super(ResUsers, self.with_context(allow_send_mail=True)).reset_password(login)

    @api.model
    def signup(self, values, token=None):
        if not token:
            # maps to the existed user
            user_existed = self.env['res.users'].search(
                [('login', '=', values.get('login'))], limit=1)
            if user_existed:
                # user exists, modify it according to values
                values.pop('login', None)
                values.pop('name', None)
                user_existed.write(values)
                if not user_existed.login_date:
                    user_existed._notify_inviter()
                return (user_existed.login, values.get('password'))
            raise OauthSignupError(
                _('Account %s not found.' % values.get('login')))
        else:
            return super().signup(values, token)

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        try:
            return super()._auth_oauth_signin(provider, validation, params)
        except OauthSignupError as e:
            raise exceptions.UserError(e.args[0])

    def _validate_password(self, password):
        if not password or True not in [True if re.fullmatch(
                constrain, password) else False for constrain in PASSWORD_CONSTRAINS]:
            raise exceptions.UserError(_('New password is invalid.'))

    def write(self, values):
        if 'password' in values:
            self._validate_password(values['password'])
        return super().write(values)

    @property
    def default_groups(self):
        return [
            'base_fastapi.group_fastapi_user',
            'project.group_project_stages',
        ]

    def _add_default_groups(self):
        group_ids = []
        for group_name in self.default_groups:
            group = self.env.ref(group_name)
            if not group:
                continue
            group_ids.append(Command.link(group.id))
        if group_ids:
            self.write({
                'groups_id': group_ids
            })

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        users._add_default_groups()
        return users

    def create_new_refresh_token(self):
        self.ensure_one()
        payload = {
            'iat': int(time.time()),
            'sub': self.uuid,
            'login': self.login,
        }
        refresh_token = jwt.generate_jwt(
            payload, tools.config.get('jwt_private_key') or 'ZHNnaF53NTY0NV4jJV4lXlEmJUdGSkRIIyY=')
        self.refresh_token_ids = [Command.create(
            {'refresh_token': refresh_token})]
        return refresh_token

    def delete_refresh_token(self, refresh_token):
        refresh_tokens = self.refresh_token_ids.filtered_domain(
            [('refresh_token', '=', refresh_token)])
        if refresh_tokens:
            self.refresh_token_ids = [Command.delete(
                rec.id) for rec in refresh_tokens]
            return refresh_token
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_('Your login has expired. Please login again.'),
            )

    @api.model
    def authenticate_refresh_token(self, refresh_token):
        db = self.env.cr.dbname
        try:
            registry = Registry(db)
            user = self.env['res.users'].with_user(SUPERUSER_ID).search(
                [('refresh_token_ids.refresh_token', '=', refresh_token)], limit=1)
            if not user:
                raise AccessDenied
            uid = user.id
            request.session.uid = None
            request.session.pre_login = user.login
            request.session.pre_uid = uid

            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, uid, {})
                # if 2FA is disabled we finalize immediately
                user = env['res.users'].browse(uid)
                if not user._mfa_url():
                    request.session.finalize(env)

            if request and request.session and request.db == db:
                # Like update_env(user=request.session.uid) but works when uid is None
                self.env = odoo.api.Environment(
                    self.env.cr, request.session.uid, request.session.context)
                request.update_context(**request.session.context)
            return self.env['res.users'].browse(uid)
        except AccessDenied:
            raise UserError(_('Your login has expired. Please login again.'))

    def _action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode') or self.env.context.get('import_file'):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        account_created_template = None
        if create_mode:
            account_created_template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            if account_created_template and account_created_template._name != 'mail.template':
                _logger.error("Wrong set password template %r", account_created_template)
                return

        email_values = {
            'email_cc': False,
            'auto_delete': False,
            'message_type': 'user_notification',
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            email_values['email_to'] = user.email
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
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
