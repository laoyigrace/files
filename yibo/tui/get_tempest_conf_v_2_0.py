import httplib2
import os
import paramiko
import re
import json
import time
from urllib import urlencode

base_dir = "/tmp"
tui_tac_host = "http://localhost:8003"


def get_openstack_ip():
    ip = None
    openstack_info_file = "%s/vmid.txt" % base_dir
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


#ip = get_openstack_ip()
ip = "100.100.0.2"
if ip is None:
    raise ValueError, "Do not get the openstack's ip"

def get_sf_version():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username="root", password="1")
    stdin, stdout, stderr = client.exec_command("cat /sf/version")
    version = stdout.read()
    version = version.replace("\r", " ")
    version = version.replace("\n", " ")
    print "[SANGFOR_VERSION]%s" % version
    return version

def get_pkg_build_version():

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username="root", password="1")
    stdin, stdout, stderr = client.exec_command("cat /etc/puppet/modules/vt-cloud/build.txt")
    version = stdout.read()
    version = version.replace("\r", "")
    version = version.replace("\n", "")
    print "[SANGFOR_PACKAGE_BUILD_VERSION]%s" % version
    return version

get_sf_version()
get_pkg_build_version()

fuel_hostname = ip
fuel_username = 'root'
fuel_password = '1'
host_path = '/etc/hosts'
local_dir = '/home/jenkins'
remote_dir = '/root'
change_db_file = 'change_db.py'


"""
def trans_files(files, method):
    # try:
    trans = paramiko.Transport((fuel_hostname, 22))
    trans.connect(username=fuel_username, password=fuel_password)
    sftp = paramiko.SFTPClient.from_transport(trans)
    if method == 'put':
        for f in files:
            sftp.put(os.path.join(local_dir, f), os.path.join(remote_dir, f))
    if method == 'get':
        for f in files:
            sftp.get(os.path.join(remote_dir, f), os.path.join(local_dir, f))
    trans.close()
    return True
    # except Exception:
    # print"connect error!"
    # return False


def auto_change_db_endpoints():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=fuel_hostname, username=fuel_username, password=fuel_password)
    if trans_files([change_db_file], 'put'):
        stdin, stdout, stderr = ssh.exec_command('python ' + os.path.join(remote_dir, change_db_file))
        if 'success' in stdout.read():
            print 'change_db success'
            return True
    return False


auto_change_db_endpoints()
"""

def get_domains(output):
    print 'get domains from ' + host_path
    ip_re_pat = re.compile(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
    domain_re_pat = re.compile(r'.*.cloud.vt')
    re_pat = re.compile(r'\s+')
    domains = []
    #output = os.popen('cat ' + host_path)
    lines = output.split("\n")
    for line in lines:
        if line is "" or line is None:
            continue
        con = {}
        pat = re_pat.findall(line)[0]
        result = line.split(pat)
        if len(result) == 2:
            ip = ip_re_pat.findall(result[0])
            domain = domain_re_pat.findall(result[1])
            if len(ip) == 1 and len(domain) == 1:
                con['ip'] = ip[0]
                con['domain'] = domain[0]
                domains.append(con)
    return domains

def get_hosts():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=fuel_hostname, username=fuel_username, password=fuel_password)
    stdin, stdout, stderr = ssh.exec_command("cat /etc/hosts")
    output = stdout.read()
    return output


def set_host():

    hosts_content = get_hosts()
    domains = get_domains(hosts_content)
    data = json.dumps(domains)

    data = {"hosts": data}
    http_client = httplib2.Http()
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    url = "%s/tac_ui/set_host" % tui_tac_host
    for i in range(10):
        resp, content = http_client.request(url, "POST", headers=headers, body=urlencode(data))

        content = json.loads(content)
        if resp["status"] == '200':
            if content["code"] == 0:
                print "Successfully set hosts"
                break
        print "Failed to set hosts, try for %s times. Error msg is :%s" % (i, content["msg"])
        time.sleep(10)

    return True


def unset_host():
    for i in range(5):
        http_client = httplib2.Http()
        resp, content = http_client.request("%s/tac_ui/unset_host" % tui_tac_host, "GET")
        content = json.loads(content)
        if resp["status"] == '200':
            if content["code"] == 0:
                print "Successfully UNset hosts"
                break
        print "Failed to UNset hosts, try for %s times. Error msg is :%s" % (i, content["msg"])
        time.sleep(5)

    return True

data = """openstack_ssh_GROUP_host=REPLACEIPADDRESSHERE&openstack_user_GROUP_name=admin&openstack_user_GROUP_password=1&openstack_tenant_GROUP_name=admin&openstack_ssh_GROUP_port=22&openstack_ssh_GROUP_username=root&openstack_ssh_GROUP_password=1"""
data = data.replace("REPLACEIPADDRESSHERE", ip)


def get_tempest_conf_file():
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

    # import pdb
    # pdb.set_trace()

    tempest_file = "%s/tempest.conf" % base_dir
    fp = open(tempest_file, "w+")
    fp.write(content)
    fp.close()

set_host()
#time.sleep(20)
get_tempest_conf_file()
unset_host()

#tempest_conf_file = "%s/tempest.conf" % base_dir
#fp = open(tempest_conf_file)
#lines = fp.readlines()
#for line in lines:
#    if re.match("log_file\s+")

