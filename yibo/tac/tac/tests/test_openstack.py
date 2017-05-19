from tac.openstack import SSH
import unittest


class TestOpenstack(unittest.TestCase):
    def setUp(self):
        self.host = "www.cpt.com"
        self.port = 22
        self.username = "root"
        self.password = "admin123"

    def test_exec_command(self):
        ssh = SSH(
               self.host,
               self.port,
               self.username,
               self.password)
        stdin, stdout, stderr = ssh.exec_command("pwd")

    def test_system(self):
        stdin, stdout, stderr = SSH.system("pwd",
               self.host,
               self.port,
               self.username,
               self.password)