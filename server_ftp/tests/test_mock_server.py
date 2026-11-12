# Copyright 2020 - 2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from io import BytesIO

from .common import MockServerCase


class TestMockServer(MockServerCase):
    """Test MockServer."""

    def test_mock_server(self):
        """Test Mock FTP Server."""
        folder = self.folder
        server = folder.server_id
        server.action_test_connection()
        self.assertEqual(server.state, "done")
        directory = folder.connect()
        self.assertEqual(directory.listdir(), [])
        datas = BytesIO()
        datas.write(b"Hello World!")
        directory.putfo(datas, "hello.txt")
        self.assertEqual(directory.listdir(), ["hello.txt"])
        self.assertTrue(directory.exists("hello.txt"))
        self.assertFalse(directory.exists("bye.txt"))
        get_datas = BytesIO()
        directory.getfo("hello.txt", get_datas)
        get_datas.seek(0)
        hello_bytes = get_datas.read()
        self.assertEqual(hello_bytes, b"Hello World!")
        directory.remove("hello.txt")
        self.assertFalse(directory.exists("hello.txt"))
        self.assertEqual(directory.listdir(), [])
        directory.close()

    def test_server_type_instances(self):
        """Every selection value maps to a server class."""
        for value, _label in self.server._fields["server_type"].selection:
            self.server.server_type = value
            self.assertTrue(self.server._make_server_instance())

    def test_multi_write_resets_state(self):
        """Connection edits on several records reset state."""
        servers = self.server | self.server.copy()
        servers.write({"state": "done"})
        servers.write({"host": "other.acme.com"})
        self.assertEqual(set(servers.mapped("state")), {"draft"})
