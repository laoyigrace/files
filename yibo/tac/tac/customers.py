import pika
import os

import values


class CustomerFileNotExist(ValueError):
    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return "The customer is not found: %s" % self.file_path


class CustomersInfo(object):
    def __init__(self, mq_host="localhost", mq_port=5672, mq_name="tac_customer_file"):
        self.mq_host = mq_host
        self.mq_port = mq_port
        self.mq_name = mq_name
        self.routing_key = self.mq_name

        self.customer_file = None

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.mq_host, self.mq_port))
        self.channel = self.connection.channel()

        self._pop_file_info()

    def _pop_file_info(self):
        """Get the msg(the path of the customers file) from the mq

        """

        for method_frame, properties, body in self.channel.consume(self.mq_name):
            print(method_frame, properties, body)
            self.customer_file = body
            self.channel.basic_ack(method_frame.delivery_tag)
            break

        requeued_messages = self.channel.cancel()
        print 'Requeued %i messages' % requeued_messages

        return self.customer_file

    def _push_file_info(self, message):
        self.channel.queue_declare(queue=self.mq_name)
        self.channel.basic_publish(exchange="", routing_key=self.routing_key, body=message)

    def close(self):
        self.connection.close()

    def _parse(self, str):
        group_name = str.split("_GROUP_")[0]
        keyvalue = str.split("_GROUP_")[-1]
        key = keyvalue.split(" = ")[0]
        value = keyvalue.split(" = ")[-1]
        value = value.replace("\n", "")

        info = {
            group_name: [
                {key: value}
            ]
        }
        return info

    def parse(self):
        if not os.path.isfile(self.customer_file):
            raise CustomerFileNotExist(self.customer_file)

        customer_info = {}
        fp = open(self.customer_file)
        lines = fp.readlines()

        for line in lines:
            tmp_info = self._parse(line)

            for (group_name, key_values) in tmp_info.items():
                if group_name in customer_info:
                    group_info = customer_info[group_name]
                    keys = values.Utils.get_dict_keys(group_info)
                    for key_value in key_values:
                        for key in key_value:
                            if key in keys:
                                continue
                            else:
                                customer_info[group_name].append({key: key_value[key]})
                else:
                    customer_info[group_name] = tmp_info[group_name]
        info = {}
        ssh_info = customer_info["openstack_ssh"]
        user_info = customer_info["openstack_user"]
        tenant_info = customer_info["openstack_tenant"]
        info["openstack"] = {
            "openstack_ssh": ssh_info,
            "openstack_user": user_info,
            "openstack_tenant": tenant_info
        }
        info["customer"] = []
        for group_name in customer_info:
            if group_name is "openstack_ssh":
                continue
            else:
                info["customer"].append({group_name:customer_info[group_name]})

        return info
