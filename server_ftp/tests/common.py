# Copyright 2020 - 2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Define a class that can be used in Custom Modules to test FTP interactions."""

from odoo.tests.common import TransactionCase


class MockServerCase(TransactionCase):
    """Test MockServer."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server = cls.env["server.ftp"].create(
            {
                "name": "Mock FTP Server for testing",
                "server_type": "mock",
                "host": "example.acme.com",
                "user": "anonymous",
                "password": "secret",
                "state": "draft",
            }
        )
        cls.folder = cls.env["server.ftp.folder"].create(
            {
                "name": "Mock FTP Folder",
                "server_id": cls.server.id,
                "path": "example_directory",
            }
        )
