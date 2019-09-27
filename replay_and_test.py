import typing
import re
from time import sleep
import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import utils as utils
import json

"""
global watch_list data
read watch_list.json into g_wl_data dictionary
Format::-
{dut_ip : {command, cmd_no, watchers}}
Ex::-
{
 "10.59.136.32": {
        "cmd": "sudo show vlan bri", 
        "cmd_no": 1, 
        "watchers": []
    }
}
"""
g_wl_dict: typing.Dict[typing.Any, typing.Any] = {}
"""
List of DUTs
"""
g_dut_ip_list: typing.List[typing.Any] = []
"""
ssh client object dictionary
each dut will have a client obj
"""
g_ssh_client_dict: typing.Dict[typing.Any, typing.Any] = {}

g_uname = 'admin'
g_pwd = 'broadcom'


def setup_automation_infra() -> None:
    """
    Read watch_list file and create all required ssh sessions.

    :return: None
    """
    global g_dut_ip_list
    global g_wl_dict

    with open('watch_list.json', 'r') as wl:
        g_wl_dict = json.load(wl)

    for key in g_wl_dict.keys():
        if key not in g_dut_ip_list:
            g_dut_ip_list.append(key)

    for dut in g_dut_ip_list:
        client = pc.SSHClient()
        g_ssh_client_dict[dut] = client

        try:
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(dut, username=g_uname, password=g_pwd)
        except Exception as e:
            utils.log_excp('Client connection Failed : {} {} {} {}'.format(dut, '22', g_uname, g_pwd))
            utils.log_excp('Received exception : {}'.format(e))
            client.close()
            sys.exit(1)

    pass


def start_automation():
    """
    Run automation from watch_list
    :return:
    """
    for key, val in g_wl_dict.items():
        client          = g_ssh_client_dict[key]
        cmd: str        = val['cmd']
        watchers: typing.List  = val['watchers']
        print('{} : executing : {}'.format(key,cmd))

        if cmd.startswith('sleep'):
            r1 = re.search(r'sleep (.*)', cmd)
            sleep(r1.groups(0))

        stdin, stdout, stderr = client.exec_command(cmd)
        lines = stderr.readlines()
        if len(lines):
            for line in lines:
                utils.log_excp('{}'.format(line.strip()))
            continue
        if cmd.startswith('sudo show'):
            ret = utils.process_show_output(cmd, stdout)
            if watchers and ret is None:
                utils.log_excp('FAILED : \n{}: {}'.format(key, val))
                return
            else:
                re_table, fsm_results = ret

            # compare show output with watchers
            for subset in watchers:
                match_found = False
                for row in fsm_results:
                    superset = dict(zip(re_table.header, row))
                    # check if subset in superset
                    if subset.items() <= superset.items():
                        match_found = True
                        break
                if not match_found:
                    utils.log_excp('match not found for'.format(subset))
                    utils.log_excp('subset : {}'.format(subset))
                    utils.log_excp('show   : {}'.format(fsm_results))
                    utils.log_excp('FAILED')
                    return

            utils.log_info('PASS')
    pass
