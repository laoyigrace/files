#!/bin/bash -xe

source /root/keystonerc_admin


# 设置默认配额
#  *** add conde here ***
nova quota-class-update --instances 200 --cores 400 --ram 81920  --snapshots 200 unauth

neutron sfrole-quota-update --subnet 200 --sf_fip_alloc 300 --port_map 100 --router_acl 100 --ipdomain 100 --sffip_qos 12800 unauth

