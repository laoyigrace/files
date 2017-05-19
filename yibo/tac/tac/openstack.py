import paramiko


class Dev(object):
    def __init__(self, info):
        self.ssh_info = self._list_to_dict(info["openstack_ssh"])
        self.host = self.ssh_info["host"]
        self.ssh_port = int(self.ssh_info["port"])
        self.ssh_username = self.ssh_info["username"]
        self.ssh_password = self.ssh_info["password"]

        self.tenant_info = self._list_to_dict(info["openstack_tenant"])
        self.tenant_name = self.tenant_info["name"]

        self.user_info = self._list_to_dict(info["openstack_user"])
        self.user_name = self.user_info["name"]
        self.user_password = self.user_info["password"]

        self.ssh = self.SSH(self.host, self.ssh_port,
                            self.ssh_username, self.ssh_password)

    @staticmethod
    def _list_to_dict(info):
        new_info = {}
        for ss in info:
            for key in ss:
                new_info[key] = ss[key]
        return new_info

    class SSH(object):

        def __init__(self,
                     host="localhost",
                     port=22,
                     username="root",
                     password="admin123",
                     ):

            self.client = None
            self.host = host
            self.port = port
            self.username = username
            self.password = password

            self._connect()

        def _connect(self,
                    host=None,
                    port=None,
                    username=None,
                    password=None):

            host = self.host if host is None else host
            port = self.port if port is None else port
            username = self.username if username is None else username
            password = self.password if password is None else password

            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(host, port, username, password)
            return self.client

        def reconnect(self):
            self.close()
            self._connect()

        def close(self):
            if self.client is not None:
                self.client.close()
                self.client = None

            return self.client

        def exec_command(self, cmd):
            stdin, stdout, stderr = self.client.exec_command(cmd)
            return stdin, stdout, stderr

        @classmethod
        def system(cls, cmd="pwd",
                 host="localhost",
                 port=22,
                 username="root",
                 password="admin123"):

            obj = cls(host, port, username, password)
            stdin, stdout, stderr = obj.exec_command(cmd)
            obj.close()
            return stdin, stdout, stderr
