from django.http import HttpResponse
from django.shortcuts import render
import json
from tac import values
import os

import time
import pika
import random
import re
import string

import paramiko

# Create your views here.


domain_host_path = "/etc/hosts"

def index(request):
    v = values.get_values_for_ui()
    # temp = tac_obj.get_defaults_runtime
    return render(
        request,
        "index.html",
        {"default_values": v}
    )


def push_msg(msg, mq_host="localhost", mq_port=5672, mq_name="tac_customer_file"):
    routing_key = mq_name
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(mq_host, mq_port))

    channel  = connection.channel()
    channel.queue_declare(queue=mq_name)
    channel.basic_publish(exchange="", routing_key=routing_key, body=msg)
    # print "[x] Sent 'Hello, World!'"
    connection.close()


def _check_host_flag():
    flag_path = "/etc/hosts.bak"
    if os.path.exists(flag_path):
        return True
    else:
        return False


def _get_domains(output):
    print 'get domains from ' + domain_host_path
    ip_re_pat = re.compile(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
    domain_re_pat = re.compile(r'(.*.cloud.vt|.*.xyclouds.cn)')
    re_pat = re.compile(r'\s+')
    domains = []

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


def _get_hosts(hostname, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname,
                username=username,
                password=password)
    stdin, stdout, stderr = ssh.exec_command("cat /etc/hosts")
    output = stdout.read()
    return output


def _set_host(request):
    if _check_host_flag():
        resp = {
            "code": 1,
            "msg": "The host is already set by others, please wait"
        }
    else:
        params = request.POST
        openstack_ip = params["openstack_ssh_GROUP_host"]
        openstack_username = params["openstack_ssh_GROUP_username"]
        openstack_password = params["openstack_ssh_GROUP_password"]

        domains_content = _get_hosts(
            openstack_ip,
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

        resp = {"code": 0,"msg": "ok"}

    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response


def unset_host(request):
    if not _check_host_flag():
        resp = {
            "code": 1,
            "msg": "The host is not set yet."
        }
    else:
        #os.system("sudo cp /etc/hosts.bak /etc/hosts")
        #os.system("sudo rm -rf /etc/hosts.bak || ls /etc")
        os.system("cp %s.bak %s" % (domain_host_path, domain_host_path))
        os.system("rm -rf /etc/hosts.bak || ls /etc")
        resp = {"code": 0,"msg": "ok"}

    response = HttpResponse(json.dumps(resp), content_type="application/json")
    return response


def create(request):
    # oslo-config-generator --config-file sf_config-generator.tempest.conf
    # --output-file ./auto_generated.conf
    curr_dir = os.path.dirname(os.path.dirname(__file__))
    tmpdir = "/tmp/"
    r_simple = random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",10)
    r_simple = string.join(r_simple).replace(" ", "")
    config_file = "%s/tac_ui/sf_config-generator.tempest.conf" % (curr_dir)
    tempest_file = "%s/tempest_%s.conf" % (tmpdir, r_simple)

    # format the post data
    post_data = request.POST

    _set_host(request)
    content = ""
    for key in post_data:
        if "_GROUP_" in key:
            # if post_data[key] is not None and post_data[key] is not u"":
            content += "%s = %s\n" % (key, post_data[key])

    # write the content to file

    customer_file = "%s/customer_%s.conf" % (tmpdir, r_simple)
    fp = open(customer_file, 'w+')
    fp.write(content)
    fp.close()

    push_msg(customer_file, "rabbitmq.cpt.com", 5672)

    # call the cmd to generate the tempest.conf
    cmd = "tac-config-generator --config-file %s " \
          "--customer-file %s " \
          "--output-file %s" % \
          (config_file, customer_file, tempest_file)

    os.system(cmd)

    # get the content of tempest.conf and delete the file

    now = time.time()
    timeout = 12
    tempest_conf_info = None

    flag = "sangforcustomer_"
    flag_comma = "s,a,n,g,f,o,r,c,u,s,t,o,m,e,r,_,"
    while time.time() - now <= timeout:
        if os.path.isfile(tempest_file) and\
                        os.path.getsize(tempest_file) != 0:
            t_fp = open(tempest_file,"r")
            lines = t_fp.readlines()
            tempest_conf_info = []
            for line in lines:
                if flag_comma in line:
                    line = line.replace(",", "")
                if flag in line:
                    line = line.replace("#", "", 1)
                    line = line.replace(flag, "")

                tempest_conf_info.append(line)
            t_fp.close()
            # delete the tmp files
            # if os.path.isfile(customer_file):
            #   os.remove(customer_file)
            if os.path.isfile(tempest_file):
                os.remove(tempest_file)
            break
        else:
            continue

    # response with the content of tempest.conf
    unset_host(request)
    resp = {
        "code": 0,
        "msg": "ok",
        "data": tempest_conf_info
    }
    # response = HttpResponse(
    # json.dumps(resp), content_type="application/json")

    response = HttpResponse(tempest_conf_info, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % (os.path.basename(tempest_file))

    return response
