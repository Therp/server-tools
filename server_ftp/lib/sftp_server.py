# Copyright 2020 - 2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import posixpath

import paramiko

from .abstract_ftp_server import AbstractFTPServer


class SFTPServer(AbstractFTPServer):
    def __init__(self):
        super().__init__()
        self.transport = None

    def connect(self, host, port, user, password):
        """Connect to object"""
        # paramiko directly, pysftp is no longer compatible
        # TODO: make this secure (host key verification)
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=user, password=password)
        self.server = paramiko.SFTPClient.from_transport(self.transport)
        return self

    def close(self):
        """Close connection"""
        if self.server:
            self.server.close()
        if self.transport:
            self.transport.close()
        self.server = None
        self.transport = None

    def putfo(self, file_like, name):
        """Transfer file-like object to server

        name: filename+extension for file at server
        file_like: byte object, content of which
        will appear in server as name
        """
        self.server.putfo(file_like, name)

    def put(self, filepath, name):
        """Transfer file object to server

        name: filename+extension for file at server
        filepath: filepath_to_file, content of which
        will appear in server as name
        """
        self.server.put(filepath, name)

    def getfo(self, name, file_like):
        """Get file from server

        name: filename of file to retrieve
        file_like: byte object to save containt
        of filename
        """
        self.server.getfo(name, file_like)

    def remove(self, file):
        """Remove file from server"""
        self.server.remove(file)

    def listdir(self, path=""):
        """List directory in path"""
        return self.server.listdir(path or ".")

    def cd(self, path):
        """Change directory"""
        self.server.chdir(path)

    def exists(self, file, path=""):
        """See if file exists in path"""
        try:
            self.server.stat(posixpath.join(path, file))
        except FileNotFoundError:
            return False
        return True
