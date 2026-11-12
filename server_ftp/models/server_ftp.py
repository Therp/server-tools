# Copyright 2020 - 2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import ftplib

import paramiko

from odoo import fields, models
from odoo.exceptions import UserError

from ..lib.ftp_server import FTPServer
from ..lib.ftp_tls_server import FTPTLSServer
from ..lib.mock_server import MockServer
from ..lib.sftp_server import SFTPServer

# Errors cd() can raise for the supported protocols
FOLDER_ERRORS = (*ftplib.all_errors, paramiko.SFTPError)


class ServerFTP(models.Model):
    _name = "server.ftp"
    _description = "Server FTP"

    name = fields.Char(required=True)
    host = fields.Char(required=True)
    user = fields.Char(required=True, default="anonymous", string="Username")
    password = fields.Char()
    port = fields.Integer(required=True, default=21)
    server_type = fields.Selection(
        selection=[
            ("ftp", "FTP"),
            ("ftpls", "FTP_TLS"),
            ("sftp", "SFTP"),
            ("mock", "Mock"),
        ],
        string="Connection protocol",
        required=True,
    )
    state = fields.Selection(
        selection=[("draft", "Not Confirmed"), ("done", "Confirmed")],
        default="draft",
        readonly=True,
        required=True,
    )
    folder_ids = fields.One2many(
        comodel_name="server.ftp.folder", inverse_name="server_id"
    )

    def write(self, vals):
        connection_fields = ["name", "user", "password", "port", "host", "server_type"]
        if any(f in vals for f in connection_fields):
            # Reset state if someone edits a connection field
            vals["state"] = "draft"
        return super().write(vals)

    def action_test_connection(self):
        """Test the outcome of connect()"""
        self.ensure_one()
        if not all([self.host, self.port, self.user, self.password]):
            raise UserError(self.env._("Make sure that required info is set"))
        try:
            server = self.connect()
        except Exception as e:
            raise UserError(str(e)) from e
        # Check if all folders are accessible
        not_accessible_folders = []
        for folder in self.folder_ids:
            try:
                server.cd(folder.path)
            except FOLDER_ERRORS:
                not_accessible_folders.append(
                    self.env._("Folder %s is not accessible", folder.name)
                )
        server.close()
        if not_accessible_folders:
            raise UserError("\n".join(not_accessible_folders))
        self.state = "done"

    def connect(self):
        """Return appropriate object based on server_type"""
        self.ensure_one()
        server = self._make_server_instance()
        server.connect(self.host, self.port, self.user, self.password)
        return server

    def _make_server_instance(self):
        """Return server class for selected type."""
        if self.server_type == "ftp":
            return FTPServer()
        # Key matches the selection value
        elif self.server_type == "ftpls":
            return FTPTLSServer()
        elif self.server_type == "sftp":
            return SFTPServer()
        elif self.server_type == "mock":
            return MockServer()
        raise UserError(self.env._("Unsupported FTP server type %s", self.server_type))
