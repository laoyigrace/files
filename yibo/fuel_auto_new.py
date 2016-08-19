# -*- coding: utf-8 -*-
import paramiko
import re
import time
import random
import os
import logging
import json

fuel_hostname = 'fuel.cpt.com'
fuel_username = 'root'
fuel_password = '1'
acloud_username = 'root'
acloud_password = '1'
fuel_api_url = 'http://172.17.19.2:8000/api'
vmp_hostname = 'h5.asv.cpt.com'
vmp_username = 'root'
vmp_password = 'admin123sangfornetwork'

# vm options
cluster = 'fb242d9a4016'
cfgstorage = '350014ee2617282a0_00900b1df684'
ostype = 'l2664'
osname = 'linux-centos'
ide0 = cfgstorage + ':120,format=qcow2,cache=directsync,preallocate=off,forecast=enable,cache_size=256'
#ide1 = cfgstorage + ':100,format=qcow2,cache=directsync,preallocate=metadata,forecast=enable,cache_size=256'
ide2 = 'none,media=cdrom'
net0 = ',bridge=dvs4b21ee6,bridgename=fuel-pxe,port=12345678,connect=on'
net1 = ',bridge=dvs957ce5a,bridgename=openstack,port=12345678,connect=on'
memory = ['16384', '16384']
node_type = ["ctl", "com"]

# fuel options
roles = ['controller', 'compute,cinder']
fuel_env_name = 'cpt'
basedir = os.path.dirname(os.path.realpath(__file__))
file_name = "/home/jenkins/vmid.txt" 
log_file = "/home/jenkins/fuel_auto_log.txt"

handler = logging.FileHandler(log_file)
fmt = "%(asctime)s-%(filename)s:%(lineno)s - %(name)s - %(message)s"
fmt = logging.Formatter(fmt)
handler.setFormatter(fmt)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)
logger.info("start fuel_auto")

# deploy env changes
def deploy_env(env_id, ssh):
    print 'deploy env,Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
    stdin, stdout, stderr = ssh.exec_command('fuel --env ' + env_id + ' deploy-changes')
    output = stdout.read()
    #tmp_output = re.sub("\n+", "\n", output)
    #print tmp_output
    for i in range(60):
        stdin, stdout, stderr = ssh.exec_command('fuel env |grep ' + fuel_env_name)
        result = stdout.read()
        if len(result.split('|'))>1 and result.split('|')[1].strip() == 'operational':
            print 'Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
            return True
        time.sleep(60)   
    return False


def delete_downline_nodes(ssh):
    stdin, stdout, stderr = ssh.exec_command('fuel node |grep False')
    result = stdout.readlines()
    if len(result) > 0:
        nodeids = []
        for i in result:
            nodeids.append(i.split('|')[0].strip())
        stdin, stdout, stderr = ssh.exec_command(
            'fuel node --node-id ' + ' '.join(nodeids) + ' --delete-from-db --force')
        if 'been deleted' in stdout.read():
            return True
        return False


# remove all nodes from env and reset env
def reset_env(env_id, env_status, ssh):
    print 'delete downline nodes'
    delete_downline_nodes(ssh)
    print 'delete env all nodes'
    stdin, stdout, stderr = ssh.exec_command('fuel node|grep ' + env_id)
    for line in stdout.readlines():
        if line.split('|')[3].strip() == env_id:
            node_id = line.split('|')[0].strip()
            stdin, stdout, stderr = ssh.exec_command('fuel node --node-id ' + node_id + ' --delete-from-db --force')
            if not 'been deleted' in stdout.read():
                print 'delete env all nodes faild,message is:' + stderr.read()
                return False
    if env_status != 'new':
        re_pat = re.compile(r'\d+')
        # reset env
        stdin, stdout, stderr = ssh.exec_command('fuel --env ' + env_id + ' reset --force')
        result = stdout.read()
        err_info = stderr.read()
        print 'get reset env task id message is:' + result
        print "The error info is:%s" % err_info
        if len(re_pat.findall(result))<1:
            print 'get reset env task id faild'
            return False            
        task_id = re_pat.findall(result)[1]
        i = 0
        print 'start reset env,Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
        while (i < 19):
            stdin, stdout, stderr = ssh.exec_command('fuel task --tid ' + task_id + ' |grep ' + task_id)
            if stdout.read().split('|')[1].strip() == 'ready':
                print 'reset env success,Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
                return True
            time.sleep(30)
            print 'reseting env ,Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
        print 'reset env faild'
        return False
    return True


# add env node
def add_env_node(env_id, mac_addr, role, ssh):
    # get node
    stdin, stdout, stderr = ssh.exec_command('fuel node list |grep ' + mac_addr[12:17] + ' -i')
    node = stdout.read()
    if node == '':
        print 'no node'
    elif not 'discover' in node:
        print 'node not discover'
    elif not 'True' in node:
        print 'node not online'
    else:
        node_cluster = node.split('|')[3].strip()
        if node_cluster != env_id and node_cluster != 'None':
            print 'node in other cluster'
        else:
            # get node id
            node_id = node.split('|')[0].strip()
            # add node
            stdin, stdout, stderr = ssh.exec_command(
                'fuel --env ' + env_id + ' node set --node ' + node_id + ' --role ' + role)
            if 'were added' in stdout.read():
                print 'node were added'
                if set_node_networks(node_id, ssh):
                    print  'node were set networks'
                    return True
                print 'node were not set networks'
                return False
            print 'node were not added'
            return False
    return False


def set_node_networks(nodeid, ssh):
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


# wait node online
def wait_node_online(mac_addr, ssh):
    i = 0
    while (i < 29):
        stdin, stdout, stderr = ssh.exec_command(
            'fuel node list |grep ' + mac_addr[12:17] + ' -i|grep True|grep discover')
        if stdout.read() != '':
            print 'node is online'
            return True
        i += 1
        print 'wait node online,sleep 30s'
        time.sleep(30)
    print 'node is not online'
    return False


# get mac addr
def get_mac_addr(ssh):
    mac_addrs = []
    for i in range(0, 4):
        stdin, stdout, stderr = ssh.exec_command('vtpsh get /cluster/gen_mac_addr')
        result = stdout.read()
        if '200 OK' not in result:
            print 'get mac_addrs faild, message is ' + stderr.read()
            return False
        mac_addrs.append(result.split('\n')[1])
    return mac_addrs


# create vm
def create_vm(options, host, ssh):
    command = 'vtpsh create /nodes/' + host + '/qemu/create ' + options
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read()
    if '200 OK' not in result:
        print 'create vm faild, message is ' + stderr.read()
        return False
    #print 'create vm message is:' + result
    if len(result.split('200 OK')[1].split(':')) > 2:
        vmid = result.split('200 OK')[1].split(':')[-3]
    else:
        print 'get vmid faild'
        return False
    return vmid


# start vm
def start_vm(vmid, host, ssh):
    command = 'vtpsh create /nodes/' + host + '/qemu/' + vmid + '/status/start'
    stdin, stdout, stderr = ssh.exec_command(command)
    if '200 OK' not in stdout.read():
        print 'start vm faild, message is ' + stderr.read()
        return False
    return True


def write_in_file(str, option):
    fp = open(file_name, option)
    fp.write(str + '\n')
    fp.close()


def get_vmp_host(ssh):
    stdin, stdout, stderr = ssh.exec_command('vtpsh get /cluster/network/cluster_iface')
    result = stdout.read()
    if not '200' in result:
        print 'get host error'
        return False
    re_pat = re.compile(r'host-[A-Za-z0-9]+')
    host = re_pat.findall(result)[0]
    print 'get host success,host is ' + host
    return host


# create node
def create_node(memory, host, ssh, node_type=""):
    #vmp_name = 'tempest_auto_' + ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890', 10))
    vmp_name = 'tempest_auto_%s_%s' % (node_type, time.time()) 
    print 'get mac addrs'
    mac_addr = get_mac_addr(ssh)
    if mac_addr:
        options = '-name ' + vmp_name + ' -dir ' + cluster + ' -cfgstorage ' + cfgstorage \
                  + ' -boot ncd -cpu host -memory ' + memory + ' -sockets 1 -cores 4 -osname ' \
                  + osname + ' -ostype ' + ostype + ' -abnormal_recovery 1 -ide0=' + ide0 + ' -ide2 ' \
                  + ide2 + ' -net0 e1000=' + mac_addr[0] + net0 + ' -net1 e1000=' + mac_addr[1] + net1 + ' -net2 e1000=' \
                  + mac_addr[2] + net1 + ' -net3 e1000=' + mac_addr[3] + net1 + ' -logo 0 -onboot 0 -uefi_bios 0'
        print 'create vm'
        vmid = create_vm(options, host, ssh)
        if vmid:
            print 'start vm'
            if start_vm(vmid, host, ssh):
                return mac_addr[0], vmid
    return False, False


# create and start nodes
def create_and_start_nodes(num):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=vmp_hostname, username=vmp_username, password=vmp_password)
    print 'get host'
    host = get_vmp_host(ssh)
    if not host:
        return False
    print 'create and start nodes ,Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
    mac_addrs = []
    vmids = []
    for i in range(0, num):
        mac_addr, vmid = create_node(memory[i], host, ssh, node_type[i])
        if mac_addr and vmid:
            mac_addrs.append(mac_addr)
            vmids.append(vmid)
        else:
            ssh.close()
            return False
        time.sleep(10)
    print 'create node success'
    write_in_file('vmids = ' + ','.join(vmids) + '\n', 'w')
    return mac_addrs


def get_public_ip(env_id, ssh):
    stdin, stdout, stderr = ssh.exec_command('fuel network --env ' + env_id + ' -d --dir /root')
    re_pat = re.compile(r'/root/.*')
    result = stdout.read().replace('\n','')
    file = re_pat.findall(result)[0]
    stdin, stdout, stderr = ssh.exec_command('cat ' + file + '|grep public_vip')
    result = stdout.read()
    re_pat = re.compile(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
    public_ip = re_pat.findall(result)
    if len(public_ip) == 1:
        print 'public_ip is ' + public_ip[0]
        return public_ip[0]
    return False


# fule deploy openstack
def fuel_deploy(mac_addrs):
    print 'Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=fuel_hostname, username=fuel_username, password=fuel_password)
    # get env
    stdin, stdout, stderr = ssh.exec_command('fuel env|grep ' + fuel_env_name)
    env = stdout.read()
    if env == '':
        print 'no env ' + fuel_env_name
    else:
        env_id = env.split('|')[0].strip()
        env_status = env.split('|')[1].strip()
        if not reset_env(env_id, env_status, ssh):
            ssh.close()
            return False
        for index, mac_addr in enumerate(mac_addrs):
            if wait_node_online(mac_addr, ssh):
                result = add_env_node(env_id, mac_addr, roles[index], ssh)
                if not result:
                    ssh.close()
                    return False
            else:
                ssh.close()
                return False
        if deploy_env(env_id, ssh):
            public_ip = get_public_ip(env_id, ssh)
            if public_ip:
                write_in_file('\npublic_ip = ' + public_ip, 'a')
                create_demo_config(public_ip)
            ssh.close()
            return True
        ssh.close()
        return False
    ssh.close()
    return False

def update_package():
    print 'Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
    print "Start update package on fule:%s" % fuel_hostname
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=fuel_hostname, username=fuel_username, password=fuel_password)
    # add by laoyi
    #stdin, stdout, stderr = ssh.exec_command("sh /root/update-online.sh")
    #output = stdout.read()
    #print output
    stdin, stdout, stderr = ssh.exec_command("cat /etc/puppet/modules/vt-cloud/build.txt")
    output = stdout.read()
    version = output.replace("\n","")
    print "[PACKAGE_VERSION_UPDATED_IN_FUEL]%s" % version
    return version

def create_demo_config(public_ip):
    print 'Time now:' + time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
    print "Start create demo on openstack:%s" % public_ip
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=public_ip, username=acloud_username, password=acloud_password)
    stdin, stdout, stderr = ssh.exec_command("cd /root/vt-cloud/;./demo-config.sh")
    output = stdout.read()
    print output
    
    return True

def main():
    version = update_package() 
    mac_addrs = create_and_start_nodes(2)
    if mac_addrs:
        if fuel_deploy(mac_addrs):
            print 'deploy openstack success'
            return True
        print 'deploy openstack faild'
    else:
        print 'create node faild'
    return False


if __name__ == '__main__':
    main()
