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
g_dut_clients: typing.Dict = {}
g_uname = 'admin'
g_pwd = 'broadcom'


class DutClients:
    """

    """
    def __init__(self, dut_ip: str, dut_name: str):
        self.dut_ip = dut_ip
        self.dut_name = dut_name
        self.log_file = open(dut_name+'_log','w')
        self.client = pc.SSHClient()

        try:
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(dut_ip, username=g_uname, password=g_pwd)
        except Exception as e:
            utils.log_excp('Client connection Failed : {} {} {} {}'.format(dut_ip, '22', g_uname, g_pwd))
            utils.log_excp('Received exception : {}'.format(e))
            self.client.close()
            sys.exit(1)
        pass

    def exec_cmd(self,cmd,watchers):
        self.log_file.writelines('\n\n>>> CMD : {}'.format(cmd))

        if cmd.startswith('sleep'):
            r1 = re.search(r'sleep (.*)', cmd)
            sleep(r1.groups(0))

        stdin,stdout,stderr = self.client.exec_command(cmd)
        lines = stderr.readlines()
        if len(lines):
            self.log_file.writelines('\nSTDERR : \n{}'.format(lines))
            for line in lines:
                utils.log_excp('{}'.format(line.strip()))
            return
        if cmd.startswith('show'):
            ret = utils.process_show_output(cmd, stdout)
            if watchers and ret is None:
                utils.log_excp('FAILED : \n{}: {}'.format(key, val))
                return
            else:
                re_table, fsm_results = ret
            self.log_file.writelines('\nFSM_RESULTS : \n{}'.format(fsm_results))

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
                    self.log_file.writelines('\n =====>>>>> FAILED : match not found for \n{}'.format(subset))
                    utils.log_excp('match not found for'.format(subset))
                    utils.log_excp('subset : {}'.format(subset))
                    utils.log_excp('show   : {}'.format(fsm_results))
                    utils.log_excp('FAILED')
                    return
                else:
                    self.log_file.writelines('\n =====>>>>> PASSED : match found for \n{}'.format(subset))
            utils.log_info('\n =====>>>>> TC PASS')
        pass


def setup_automation_infra() -> None:
    """
    Read watch_list file and create all required ssh sessions.

    :return: None
    """
    global g_dut_ip_list
    global g_wl_dict

    wl = open('watch_list.json', 'r')
    try:
        g_wl_dict = json.load(wl)
    except Exception as e:
        wl.close()
        utils.log_info('File Not in proper JSON format, append } at end')
        with open('watch_list.json', 'a') as f:
            f.writelines('}')
            f.close()
        with open('watch_list.json', 'r') as wl:
            g_wl_dict = json.load(wl)

    keys = set([dut_ip_cmd_no[:-2] for dut_ip_cmd_no in g_wl_dict.keys()])

    for idx,dut_ip in enumerate(keys):
        dc = DutClients(dut_ip, 'D'+str(idx))
        g_dut_clients[dut_ip] = dc

    pass


def start_automation() -> None:
    """
    Run automation from watch_list
    :return:
    """
    for dut_ip_cmd_no, val in g_wl_dict.items():
        dut_ip = dut_ip_cmd_no[:-2]
        dc          = g_dut_clients[dut_ip]
        cmd: str    = val['cmd']
        watchers: typing.List  = val['watchers']
        print('{} : executing : {}'.format(dut_ip_cmd_no,cmd))

        dc.exec_cmd(cmd,watchers)

    pass
