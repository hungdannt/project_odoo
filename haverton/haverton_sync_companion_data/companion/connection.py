# Docs: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/connection-string-keywords-and-data-source-names-dsns?view=sql-server-ver16
import logging

from odoo.exceptions import UserError
from odoo.http import request
from sqlalchemy import URL, create_engine, event
from sqlalchemy.engine import Engine

from .models import HistoryChangeData

_logger = logging.getLogger(__file__)


@event.listens_for(Engine, "after_execute")
def receive_after_execute(conn, clauseelement, multiparams, params, execution_options, result):
    """
    Saves info of all executed changed SQL commands
    Docs: https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.ConnectionEvents.after_execute
    """
    if any([clauseelement.is_insert, clauseelement.is_update, clauseelement.is_delete]) and clauseelement.table != HistoryChangeData.__tablename__:
        status = 'success'
        new_log = request.env['companion.sync.log'].sudo().create({
            'statement': clauseelement,
            'params': params,
            'multiparams': multiparams,
            'status': status,
            'user_id': request.env.user.id,
        })
        request.env.context = dict(
            request.env.context, companion_sync_log=new_log)


class Connection():
    def __init__(self):
        company = request.env.user.company_id
        server = company.companion_db_host
        if company.companion_db_port:
            server += ',%s' % company.companion_db_port
        database = company.companion_db_database
        username = company.companion_db_username
        password = company.companion_db_password
        self.engine = self._connect(server, database, username, password)

    def _connect(self, server, database, username, password):
        try:
            connection_string = 'TrustServerCertificate=YES;Encrypt=YES;DRIVER={ODBC Driver 18 for SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s' % (
                server, database, username, password)
            connection_url = URL.create(
                "mssql+pyodbc", query={"odbc_connect": connection_string})
            return create_engine(connection_url)
        except Exception as e:
            _logger.error(e)
            raise (UserError(e))
