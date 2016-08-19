import logging
import os
import pkg_resources
import random
import re
import time
import json
import string
import paramiko

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %('
                           'message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/home/jenkins/data/logs_all/fuelauto_%s.log' %
                             time.strftime("%Y-%m-%d--%H:%M:%S"),
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

LOG = logging.getLogger(__name__)

acloud_username = 'root'
acloud_password = '1'
fuel_hostname = "200.200.115.35"
fuel_username = "root"
fuel_password = "1"
fuel_api_url = 'http://172.17.19.2:8000/api'

def logging_time(reason="time"):
    time_now = time.strftime("%Y/%m/%d_%H:%M:%S")
    LOG.info("[TIME]%s,%s" % (time_now, reason))

def update_package():
    LOG.info('Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(
        time.time())))
    LOG.info("Start update package on fule:%s" % fuel_hostname)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=fuel_hostname, username=fuel_username, password=fuel_password)
    #stdin, stdout, stderr = ssh.exec_command("sh /root/update-online.sh")
    #output = stdout.read()
    #print output
    stdin, stdout, stderr = ssh.exec_command("cat /etc/puppet/modules/vt-cloud/build.txt")
    output = stdout.read()
    version = output.replace("\n","")
    LOG.info("[PACKAGE_VERSION_UPDATED_IN_FUEL]%s" % version)
    return version

def create_demo_config(public_ip):
    LOG.info('Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(
        time.time())))
    LOG.info("Start create demo on openstack:%s" % public_ip)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=public_ip, username=acloud_username, password=acloud_password)
    stdin, stdout, stderr = ssh.exec_command("cd /root/vt-cloud/;./demo-config.sh")
    output = stdout.read()
    LOG.info("exec demo-config result = %s", output)

    LOG.info("begin to update quota...")
    stdin, stdout, stderr = ssh.exec_command("source /root/keystonerc_admin;"
    "nova quota-class-update --instances 200 --cores 400 --ram 81920  --snapshots 200 unauth;"
    "neutron sfrole-quota-update --subnet 10 --sf_fip_alloc 300 --port_map "
                                             "100 --router_acl 100 --ipdomain 100 --sffip_qos 128000 unauth")
    output = stdout.read()
    LOG.info("end update quota, result = %s", output)

    return True

package_version = update_package()


def set_fuleclient(server_addr, **kwargs):
    LOG.info("To set the fuel server with %s" % server_addr)
    port = kwargs.get("port", 8000)
    keystone_user = kwargs.get("keystone_user", "admin")
    keystone_passwrd = kwargs.get("keystone_pass", "admin")

    custom_settings_file = os.getenv('FUELCLIENT_CUSTOM_SETTINGS')
    if custom_settings_file:
        LOG.debug("The custom file is already setting in env "
                     "FUELCLIENT_CUSTOM_STTINGS:%s") % custom_settings_file
        return custom_settings_file

    default_settings_file = pkg_resources.resource_filename("fuelclient",
                                                    "fuel_client.yaml")

    if not os.path.exists(default_settings_file):
        default_settings_file = pkg_resources.resource_filename("fuelclient", "fuelclient_settings.yaml")
    if not os.path.exists(default_settings_file):
        raise Exception("DO not get the fuelclient settings yaml file")
    if not os.path.exists(default_settings_file):
        raise ValueError, "Do not get the setting file:%s" % \
                          default_settings_file

    content = ""
    with open(default_settings_file, 'r') as default_config:
        content = default_config.readlines()

    def replace(line, rep):
        tmp = line.split(":")
        strs = "%s: \"%s\"" % (tmp[0], rep)
        return strs

    new_content = ""
    for line in content:
        if re.search("SERVER_ADDRESS", line):
            strs = replace(line, server_addr)
        elif re.search("LISTEN_PORT", line):
            strs = replace(line, port)
        elif re.search("KEYSTONE_USER", line):
            strs = replace(line, keystone_user)
        elif re.search("KEYSTONE_PASS", line):
            strs = replace(line, keystone_passwrd)
        else:
            strs = line
        new_content = "%s%s\n" % (new_content, strs)

    ran = random.Random()
    random_str = "".join(ran.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", 5))
    custom_settings_file = "%s_%s.txt" % (time.strftime("%Y%m%d_%H%M%S"), random_str)
    custom_settings_file = os.path.join("/tmp", custom_settings_file)

    with open(custom_settings_file, "w") as fp:
        fp.write(new_content)

    LOG.info("New custtom settings file is generated:%s" %
                 custom_settings_file)

    LOG.info("The settings content is: %s" % new_content)
    os.environ["FUELCLIENT_CUSTOM_SETTINGS"] = custom_settings_file
    return custom_settings_file

set_fuleclient(fuel_hostname)
# debug
# os.environ["FUELCLIENT_CUSTOM_SETTINGS"] = \
#     "/home/kgra/pythonworkspace/fuelclient_test/fuel_client.yaml"


# must import after set_fuelclient
from fuelclient.v1 import environment as fuel_env_client
from fuelclient.v1 import node as fuel_node_client
from fuelclient.objects import environment as env_objects
from fuelclient.objects import node as  fuel_node_object
from fuelclient import objects


class EnvNotFoundError(Exception):
    pass


class SFEnvironmentClient(fuel_env_client.EnvironmentClient):

    _entity_wrapper = objects.Environment

    _updatable_attributes = ('name',)

    def __init__(self):
        super(SFEnvironmentClient, self).__init__()

    def get_env_by_name(self, name):
        env_infos = self.get_all()
        for env_info in env_infos:
            if env_info["name"] == name:
                return env_info
        raise EnvNotFoundError, "Do not get the env by name:%s" % name

    def get_env_by_id(self, env_id):
        env_infos = self.get_all()
        for env_info in env_infos:
            if env_info["id"] == env_id:
                return env_info
        raise EnvNotFoundError, "Do not get the env by id:%s" % env_id

    def get_id_by_name(self, name):
        env_info = self.get_env_by_name(name)

        return env_info["id"]

    def get_status_by_name(self):
        pass

    def get_status_by_id(self, environment_id):
        env_info = self.get_env_by_id(environment_id)
        return env_info["status"]

    def reset(self, environment_id, block=False, interval=60, time_count=15):
        LOG.debug("To reset environment with id:%s"  % environment_id)
        t_env_obj = self._entity_wrapper(obj_id=environment_id)
        task_obj = t_env_obj.reset()
        if task_obj and task_obj.id:
            if block:
                self.wait_reset(task_obj, interval, time_count)
            return task_obj.id

        raise Exception, "Error occured when reset the env:%S" % environment_id

    @staticmethod
    def wait_reset(task_obj, interval=60, time_count=15):
        # after wait_reset
        for i in range(time_count):
            LOG.debug("The %s/%s time to check reset(%ss/per)" %
                          (i+1, time_count, interval))
            if task_obj.status == "ready":
                return True
            time.sleep(interval)

        raise Exception("after %s second, the task status of env reset "
                        "is not ready. It's %s" % (10*60, task_obj.status))

    def wait_deploy(self, environment_id, interval=60, time_count=60):
        for index in range(time_count):
            try:
                LOG.debug("The %s/%s time to check reset(%ss/per)" %
                              (index+1, time_count, interval))
                time.sleep(interval)
                status = self.get_status_by_id(environment_id)
                if status == "operational":
                    LOG.info("Deploy Successfully")
                    return True
            except:
                continue
        raise Exception, "The env(%s) was not deployed after %s seconds" % \
                         (environment_id, interval * time_count)

    
class SFNodeClient(fuel_node_client.NodeClient):
    _entity_wrapper = objects.Node
    _updatable_attributes = ('hostname', 'labels', 'name')

    def __init__(self):
        super(SFNodeClient, self).__init__()

    def filter_nodes_mac_addr(self, nodes, mac_addrs=[]):
        filtered_nodes = self.filter_nodes(nodes, type="mac", filter=mac_addrs)
        return filtered_nodes

    @staticmethod
    def filter_nodes(nodes, type=None, filter=[]):
        filtered_nodes = []
        for node in nodes:
            if node[type] in filter:
                filtered_nodes.append(node)

        return filtered_nodes

    def wait_for_online(self, mac_addrs, interval=30, time_count=30):
        # TODO: check the counts and interval
        for i in range(time_count):
            LOG.debug("The %s/%s time to check nodes all online.(%ss/per)"
                         % (i+1, time_count, interval))
            online_nodes = []
            tmp_nodes = self.get_all()
            tmp_nodes = self.filter_nodes_mac_addr(tmp_nodes, mac_addrs)
            all_online = True
            mac_found = []
            for mac in mac_addrs:
                for t_node in tmp_nodes:
                    if self.node_mac_is(mac, t_node):
                        if mac not in mac_found:
                            mac_found.append(mac)
                        if self.node_online(t_node):
                            online_nodes.append(t_node)
                            LOG.debug("The mac_addr is online:%s" % mac)
                        else:
                            all_online = False
                            LOG.warn("Mac:%s,status:%s, online:%s " %
                                         (mac, t_node["status"],
                                          t_node["online"]))
                        break
                if mac_found:
                    continue
                else:
                    LOG.warn("do not found the node whose mac is %s" % mac)

            if all_online and len(mac_found) == len(mac_addrs):
                LOG.debug("all nodes are on line")
                return online_nodes
            time.sleep(interval)
        raise Exception("After %s seconds, some node is still not online"
                        % (time_count * interval))

    @staticmethod
    def node_role_is(roles, node):
        if node["roles"] == roles:
            return True
        else:
            return False

    @staticmethod
    def node_status_is(status, node):
        if node["status"] == status:
            return True
        else:
            return False

    def nodes_status_are(self, status, nodes):
        flag = 0
        for node in nodes:
            if self.node_status_is(status, node):
                flag += 1
        if flag == len(nodes):
            return True
        else:
            return False

    @staticmethod
    def node_mac_is(mac, node):
        if node["mac"] == mac:
            return True
        else:
            return False

    @staticmethod
    def node_online(node):
        return node["online"]

    @staticmethod
    def delete(node_id):
        LOG.debug("To delete nodes with id:%s" % node_id)
        node_obj = fuel_node_object.Node(node_id)
        node_obj.delete()

    def delete_nodes_by_mac_addrs(self, mac_addrs):
        LOG.debug("To delete nodes with mac address:%s" % mac_addrs)
        nodes = self.get_all()
        nodes = self.filter_nodes_mac_addr(nodes, mac_addrs)
        for node in nodes:
            self.delete(node["id"])


def get_env_client():
    return SFEnvironmentClient()


def get_node_client():
    return SFNodeClient()


def set_node_networks(nodeid):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=fuel_hostname, username=fuel_username, password=fuel_password)
    stdin, stdout, stderr = ssh.exec_command('FUELCLIENT_CUSTOM_SETTINGS=/etc/fuel/client/config.yaml fuel token')
    token = stdout.read()
    cmd = 'curl --cookie "i18next=zh-CN; token=' + token + '"   ' + fuel_api_url + '/nodes/' + nodeid + '/interfaces'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    result = stdout.read()
    options = make_args(json.loads(result))

    if options:
        cmd = "curl -XPUT --cookie 'i18next=zh-CN; token=" + token + "' -d '" + json.dumps(options) + "' " + fuel_api_url + "/nodes/" + nodeid + "/interfaces"

        stdin, stdout, stderr = ssh.exec_command(cmd)
        if 'fuelweb_admin' in stdout.read():
            return True
    return False

def make_args(options):
    if len(options) < 1:
        return False
    for eth in options:
        for net in eth['assigned_networks']:
            if net['name'] == 'fuelweb_admin':
                fuelweb_admin_arg = net
            elif net['name'] == 'management':
                management_arg = net
            elif net['name'] == 'private':
                private_arg = net
            elif net['name'] == 'public':
                public_arg = net
            elif net['name'] == 'storage':
                storage_arg = net
        eth['assigned_networks']=[]
    
    options[0]['assigned_networks']=[fuelweb_admin_arg, management_arg]
    options[1]['assigned_networks']=[public_arg]
    options[2]['assigned_networks']=[storage_arg]
    options[3]['assigned_networks']=[private_arg]

    return options


# mac_addrs = ["fe:fc:fe:d3:b6:26", "fe:fc:fe:6b:fa:d4"]
mac_addrs = ["a0:36:9f:03:43:cf", "a0:36:9f:03:3f:1b"]
roles = ["controller", "compute,cinder"]

env_client = get_env_client()
node_client = get_node_client()
env_id = env_client.get_id_by_name("smoke")

logging_time("reset the env with id:%s" % env_id)
# node_client.delete_nodes_by_mac_addrs(mac_addrs)
# env_client.reset(env_id, block=True)

logging_time("wait for nodes online after reset")
# nodes = node_client.wait_for_online(mac_addrs)

# check nodes'status is discover
#status = "discover"
#if not node_client.nodes_status_are(status, nodes):
#    raise Exception, "The status of nodes are not all %s.The nodes info is " \
#                     "as follows:\n%s" % (status, nodes)
#if len(nodes) != len(roles):
#    raise Exception, " %s nodes are found, but  %s roles are set" % \
#                     (len(nodes), len(roles))

logging_time("add nodes to the env with id:%s" % env_id)
#for index, node in enumerate(nodes):
#    ret = env_client.add_nodes(env_id, [node["id"]], [roles[index]])
#    if not set_node_networks(str(node["id"])):
#        raise Exception, " %s node is found, but set networks faild" %
# node["id"]

logging_time("deploy nodes of the env with id:%s" % env_id)
#ret = env_client.deploy_changes(env_id)
#env_client.wait_deploy(env_id)

logging_time("get public ip of the env with id:%s" % env_id)
env_obj = env_objects.Environment(env_id)
network_data = env_obj.get_network_data()
public_ip = network_data["public_vip"]
LOG.info("The public ip is:%s" % public_ip)

LOG.info("begin to exec demo-config.sh")
create_demo_config(public_ip)
LOG.info("success to exec demo-config.sh")

LOG.info("writting the public ip to file:%s" % public_ip)
common_file = "/home/jenkins/vmid.txt"
#common_file = "/tmp/vmid.txt"
fp = open(common_file, "a")
fp.write("\npublic_ip = %s" % public_ip)
fp.close()

