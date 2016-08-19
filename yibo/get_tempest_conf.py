import httplib2
import os
import paramiko
import re
import json
import sys
import time
from urllib import urlencode
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %('
                           'message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/var/log/get_tempest_conf_%s.log' %
                             time.strftime("%Y-%m-%d--%H:%M:%S"),
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

LOG = logging.getLogger(__name__)

base_dir = os.path.dirname(os.path.realpath(__file__))
tui_tac_host = "http://www.cpt.com:8003"
domain_host_path = "/etc/hosts"


def get_openstack_ip():
    ip = None
    openstack_info_file = "/home/jenkins/vmid.txt"
    if not os.path.exists(openstack_info_file):
        return None
    fp = open(openstack_info_file, "r")
    lines = fp.readlines()
    fp.close()
    for line in lines:
        if re.search(r"public_ip =", line):
            ip = line.split("=")
            ip = ip[-1]
            ip = ip.replace(" ", "")
            ip = ip.replace("\n", "")
            return ip


def get_sf_version(hostname="localhost"):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, username="root", password="1")
    stdin, stdout, stderr = client.exec_command("cat /sf/version")
    version = stdout.read()
    version = version.replace("\r", " ")
    version = version.replace("\n", " ")
    LOG.info("[SANGFOR_VERSION]%s" % version)
    return version


def get_pkg_build_version(hostname="localhost"):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, username="root", password="1")
    stdin, stdout, stderr = client.exec_command("cat /etc/puppet/modules/vt-cloud/build.txt")
    version = stdout.read()
    version = version.replace("\r", "")
    version = version.replace("\n", "")
    LOG.info("[SANGFOR_PACKAGE_BUILD_VERSION]%s" % version)
    return version


def _get_domains(output):
    LOG.info('get domains from ' + domain_host_path)
    ip_re_pat = re.compile(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
    domain_re_pat = re.compile(r'(.*\.cloud\.vt|.*\.xyclouds\.cn|.*\.acloud\.vt)')
    re_pat = re.compile(r'\s+')
    domains = []

    lines = output.split("\n")
    for line in lines:
        if line is "" or line is None:
            continue
        con = {}
        pat = re_pat.findall(line)[0]
        result = line.split(pat)
        if len(result) == 2 or len(result) == 3:
            ip = ip_re_pat.findall(result[0])
            domain = domain_re_pat.findall(result[1])
            if len(ip) == 1 and len(domain) == 1:
                con['ip'] = ip[0]
                con['domain'] = domain[0]
                domains.append(con)
    return domains


def _get_hosts(hostname, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname,
                username=username,
                password=password)
    stdin, stdout, stderr = ssh.exec_command("cat /etc/hosts")
    output = stdout.read()
    return output


def _set_host(openstack_hostname, openstack_username, openstack_password):
    domains_content = _get_hosts(
        openstack_hostname,
        openstack_username,
        openstack_password
    )
    domains = _get_domains(domains_content)

    tmp_str = ""
    for domain in domains:
        tmp_str += "%s\t%s\n" % (domain["ip"], domain["domain"])
    os.system("cp %s %s.bak" % (domain_host_path, domain_host_path))

    # change /etc/hosts
    host_file = open(domain_host_path, "a")
    content = "# Set by tui-tac autoly, for get tempest config\n" + tmp_str
    host_file.write(content)
    host_file.close()
    return True


def unset_remote_host():
    for i in range(5):
        http_client = httplib2.Http()
        resp, content = http_client.request("%s/tac_ui/unset_host" % tui_tac_host, "GET")
        content = json.loads(content)
        if resp["status"] == '200':
            if content["code"] == 0:
                LOG.info("Successfully UNset hosts")
                break
        LOG.info("Failed to UNset hosts, try for %s times. Error msg is :%s" % (i, content["msg"]))
        time.sleep(5)

    return True


def unset_local_host():
    os.system("cp %s.bak %s" % (domain_host_path, domain_host_path))
    os.system("rm -rf %s.bak || ls /etc" % domain_host_path)

    return True

def get_tempest_conf_file(data):
    h = httplib2.Http()
    body = {}
    key_values = data.split("&")
    for key_value in key_values:
        key = key_value.split("=")[0]
        value = key_value.split("=")[-1]
        body[key] = value

    headers = {"Content-type": "application/x-www-form-urlencoded"}
    resp, content = h.request("%s/tac_ui/create" % tui_tac_host, "POST", headers=headers, body=urlencode(body))
    # resp, content = h.request("http://localhost:8082/tac_ui/create", "POST", headers=headers, body=body)

    tempest_file = "%s/tempest.conf" % base_dir
    fp = open(tempest_file, "w+")
    fp.write(content)
    fp.close()

def main(argv):
    if len(argv) >= 2:
        ip = argv[1]
    else:
        ip = get_openstack_ip()
        #ip = "100.35.0.2"
    if ip is None:
        raise ValueError, "Do not get the openstack's ip"

    get_sf_version(ip)
    get_pkg_build_version(ip)

    openstack_hostname = ip
    openstack_username = 'root'
    openstack_password = '1'

    data = """openstack_ssh_GROUP_host=REPLACEIPADDRESSHERE&openstack_user_GROUP_name=admin&openstack_user_GROUP_password=Admin12345&openstack_tenant_GROUP_name=admin&openstack_ssh_GROUP_port=22&openstack_ssh_GROUP_username=root&openstack_ssh_GROUP_password=1"""
    data = data.replace("REPLACEIPADDRESSHERE", ip)

    _set_host(openstack_hostname, openstack_username, openstack_password)
    #time.sleep(20)
    get_tempest_conf_file(data)
    #unset_host()


#tempest_conf_file = "%s/tempest.conf" % base_dir
#fp = open(tempest_conf_file)
#lines = fp.readlines()
#for line in lines:
#    if re.match("log_file\s+")

if __name__ == "__main__":
    argvs = sys.argv
    main(argvs)
