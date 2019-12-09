import typing
import re
from time import sleep
import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import utils as utils
import json
from topo import dut_connections as dcon
import datetime


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

class DutClients:
    def __init__(self, dut_name: str, hostip: str, port: str, uname: str, pwd: str):
        self.uname = uname
        self.pwd = pwd
        self.hostip = hostip
        self.port = port
        self.dut_name = dut_name
        self.log_file = open(dut_name+'_log','w')

        try:
            self.client = pc.SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(self.hostip, username=self.uname, password=self.pwd, timeout=10)
            transport = self.client.get_transport()
            self.chan = transport.open_session()
            self.chan.get_pty()
            self.chan.invoke_shell()

        except Exception as e:
            utils.log_excp('Client connection Failed : {} {} {} {}'.format(hostip, port, uname, pwd))
            utils.log_excp('Received exception : {}'.format(e))
            self.client.close()
            sys.exit(1)
            pass

    def syslog(self, opcode, line):
        self.log_file.writelines('\n{} : {:>15} :: {}'.format(datetime.datetime.now(), opcode, line))
        if opcode == 'ERR':
            utils.log_err(line)
        if opcode == 'INFO':
            utils.log_info(line)

    def abort_test(self):
        if utils.g_pdb_set:
            import pdb
            pdb.set_trace()
        else:
            self.syslog('ERR', 'Aborting Test')
            exit(0)

    def exec_cmd(self,cmd,watchers):
        self.syslog('CMD',cmd)

        if cmd.startswith('sudo sleep'):
            r1 = re.search(r'sleep (.*)', cmd)
            sleep(r1.groups(0))

        try:
            stdout = utils.run_command(self.chan, cmd)
        except Exception as e:
            utils.log_excp('Command execution Failed')
            utils.log_excp('Received exception : {}'.format(e))
            return

        if cmd.startswith(utils.show_cmd_pattern):
            ret = utils.process_show_output(cmd, stdout)
            if watchers and ret is None:
                self.syslog('ERR', 'Failed to Process show output for {}'.format(cmd))
                return
            else:
                re_table, fsm_results = ret
            self.syslog('INFO', fsm_results)

            # compare show output with watchers
            for subset in watchers:
                match_found = False
                superset = {}
                for row in fsm_results:
                    superset = dict(zip(re_table.header, row))
                    # check if subset in superset
                    if subset.items() <= superset.items():
                        match_found = True
                        break
                if not match_found:
                    self.syslog('ERR', 'Test FAILED: ')
                    self.syslog('ERR', 'Expected : {}'.format(subset))
                    self.syslog('ERR', 'Actual   : {}'.format(superset))
                    self.abort_test()
                else:
                    self.syslog('INFO','match found {}'.format(subset))
            self.syslog('INFO', 'TestCase PASSED')
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

    """
    keys = set([dut_ip_cmd_no[:-2] for dut_ip_cmd_no in g_wl_dict.keys()])

    for idx,dut_ip in enumerate(keys):
        dc = DutClients(dut_ip, 'D'+str(idx))
        g_dut_clients[dut_ip] = dc
    """
    for dut_cmdno in g_wl_dict.keys():
        dut = dut_cmdno.split('-')[0]
        dc = DutClients(dut, dcon[dut]['ip'], '22', 'admin', 'broadcom')
        g_dut_clients[dcon[dut]['ip']] = dc

    pass


def start_automation() -> None:
    """
    Run automation from watch_list
    :return:
    """
    for dut_cmdno, val in g_wl_dict.items():
        dut = dut_cmdno.split('-')[0]
        dut_ip = dcon[dut]['ip']
        dc          = g_dut_clients[dut_ip]
        cmd: str    = val['cmd']
        watchers: typing.List  = val['watchers']
        utils.log_info('{} : executing : {}'.format(dut_cmdno,cmd))

        dc.exec_cmd(cmd,watchers)

    pass
