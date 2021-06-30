from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from pprint import pprint
import os
if os.path.exists('/root/Lab/NeXT_UI/Test_NeXt_UI/app/data.js'):
    os.remove('/root/Lab/NeXT_UI/Test_NeXt_UI/app/data.js')

nr = InitNornir(config_file='config.yaml')


nodes = []
links= []
def get_host_info():
    global output
    try:
        output = nr.run(task=netmiko_send_command,
                        command_string='show version', use_textfsm=True)
        node_id = 0
        with open('/root/Lab/NeXT_UI/Test_NeXt_UI/app/data.js', 'a') as f:
            f.write('var topologyData = {\n"nodes":\n')
            for key, value in output.items():
                nodes_dict = {}
                global host_names
                # print(output[key].result[0]['hostname'])
                host_names = output[key].result[0]['hostname']
                mgmt_ip = nr.inventory.hosts[key].hostname
                # print(host_names,mgmt_ip)
                nodes_dict.update({
                    "id": node_id,
                    "name": host_names,
                    "mgmt_ip": mgmt_ip,
                })
                node_id += 1
                nodes.append(nodes_dict)
            # print(nodes)
            f.write(str(nodes))
            f.write(',\n')
    except:
        print(nr.inventory.hosts['hostname'] + 'unreachable')


get_host_info()

def get_link_info():
    try:
        output2 = nr.run(task=napalm_get, getters=['lldp_neighbors'])
    #    print_result(output2)
    #    print(output2['sw29'].result['lldp_neighbors']['Ethernet0/3'])
    #    ipdb.set_trace()
        for key0,value in output2.items():
            result_link_info = output2[key0].result['lldp_neighbors']
            # print(result_link_info)
            # print(type(result_link_info))
            for key1,value1 in result_link_info.items():
                link_dict = {}
                r1=result_link_info[key1]
                host_names = output[key0].result[0]['hostname']
                # print(r1)
                for i in r1:
                    # print(i['hostname'])
                    link_dict.update({
                        "source": host_names,
                        "target": i['hostname'],
                    })
                    links.append(link_dict)
    except:
        print( nr.inventory.hosts['hostname'] + 'unreachable')
get_link_info()

def link_same(dict1,dict2):
    if (dict1['source'] == dict2['target']) and (dict2['source'] == dict1['target']):
        return True
    else:
        return False
def links_result(list:links):
    new_links = []
    length = len(links)
    # print(length)
    # print(links[1])
    with open('/root/Lab/NeXT_UI/Test_NeXt_UI/app/data.js', 'a') as f:
        f.write('"links":\n')
        for i in range(length):
            flag = 0
            # print(i)
            for j in range(i+1,length):
                if link_same(links[i],links[j]):
                    flag=1
            if flag != 1:
                new_links.append(links[i])
        # new_links_info=pprint(new_links)
        f.write(str(new_links))
        f.write(',\n};')
        return new_links

links_result(list)


