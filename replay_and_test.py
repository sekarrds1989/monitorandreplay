import typing
import re
from time import sleep
import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import utils as utils
import json
import datetime
from tabulate import tabulate

from topo import dut_connections as dcon

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


def r_syslog(opcode, line):
    if opcode == 'ERR':
        utils.r_log_err(line)
    if opcode == 'INFO':
        utils.r_log_info(line)


class DutClients:
    def __init__(self, dut_name: str, hostip: str, port: str, uname: str, pwd: str):
        self.uname = uname
        self.pwd = pwd
        self.hostip = hostip
        self.port = port
        self.dut_name = dut_name
        self.log_file = open('logs/' + dut_name + '.log', 'w')

        try:
            self.client = pc.SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(self.hostip, username=self.uname, password=self.pwd, timeout=10)
            transport = self.client.get_transport()
            self.chan = transport.open_session()
            self.chan.get_pty()
            self.chan.invoke_shell()

        except Exception as e:
            utils.r_log_excp('Client connection Failed : {} {} {} {}'.format(hostip, port, uname, pwd))
            utils.r_log_excp('Received exception : {}'.format(e))
            self.client.close()
            sys.exit(1)
            pass

    def syslog(self, op_code, line):
        self.log_file.writelines('\n{} : {:>15} :: {}'.format(datetime.datetime.now(), op_code, line))
        if op_code == 'ERR':
            utils.r_log_err(line)
        if op_code == 'INFO':
            utils.r_log_info(line)

    def abort_test(self):
        if utils.g_pdb_set:
            import pdb
            pdb.set_trace()
        self.syslog('ERR', 'Aborting Test')
        sys.exit(1)

    def exec_cmd(self, tc_id, cmd, exp_op_list):
        self.syslog('CMD', cmd)

        if cmd.startswith('sudo sleep'):
            r1 = re.search(r'sudo sleep (?!$)([\d]*[.]?(?!$)[\d]*)', cmd)
            if len(r1.groups()) == 1:
                self.syslog('INFO', 'Sleep {}'.format(r1.groups()[0]))
                sleep(float(r1.groups()[0]))
                return

        try:
            stdout = utils.run_command(self.chan, cmd)
            if 'error' in stdout:
                self.syslog('ERR', stdout)
        except Exception as e:
            utils.r_log_excp('Command execution Failed')
            utils.r_log_excp('Received exception : {}'.format(e))
            return

        if cmd.startswith(utils.show_cmd_pattern):
            ret = utils.process_show_output(cmd, stdout)
            if exp_op_list and ret is None:
                self.syslog('ERR', 'Failed to Process show output for {}'.format(cmd))
                return
            else:
                re_table, fsm_results = ret

            key_col_name = ''
            for exp_op in exp_op_list:
                if 'watch-key' in exp_op.keys():
                    key_col_name = exp_op['watch-key']
                    continue

                entry_w_key = {}
                actual_op = {}
                match_found = False
                for row in fsm_results:
                    actual_op = dict(zip(re_table.header, row))
                    if key_col_name == 'NA':
                        if exp_op.items() <= actual_op.items():
                            match_found = True
                            break
                    else:
                        if actual_op[key_col_name] == exp_op[key_col_name]:
                            entry_w_key = actual_op
                            # check if exp_op is a subset of actual op
                            if exp_op.items() <= actual_op.items():
                                match_found = True
                                break

                if not match_found:
                    if key_col_name != 'NA' and not entry_w_key:
                        self.syslog('ERR', 'Entry with key({}:{}) not Found'.format(key_col_name, exp_op[key_col_name]))
                    else:
                        if not entry_w_key:
                            p_dict = actual_op
                        else:
                            p_dict = entry_w_key

                        header = ['output']
                        diff_table = [['Exp'], ['Actual']]
                        for key in p_dict.keys():
                            header.append(key)
                            diff_table[0].append(exp_op[key])
                            diff_table[1].append(p_dict[key])
                        self.syslog('ERR', ' Exp Vs Actual \n {}'.format(tabulate(diff_table, headers=header
                                                                                  , showindex='always'
                                                                                  , tablefmt='psql')))
                    self.syslog('ERR', 'Test {} FAILED'.format(tc_id))
                    self.abort_test()

            self.syslog('INFO', 'Test {} PASSED'.format(tc_id))
        pass


def read_commands_from_file(wl_file):
    global g_wl_dict

    r_syslog('INFO', 'Read commands from : {}'.format(wl_file))
    wl = open(wl_file, 'r')
    try:
        g_wl_dict = json.load(wl)
    except Exception:
        wl.close()
        r_syslog('INFO', 'File Not in proper JSON format, append } at end')
        with open(wl_file, 'a') as f:
            f.writelines('}')
            f.close()
        with open(wl_file, 'r') as wl:
            g_wl_dict = json.load(wl)


def start_automation(test_suite_name, tc_name='') -> None:
    """
    Read watch_list file and create all required ssh sessions.

    :return: None
    """
    global g_dut_ip_list

    for dut in dcon.keys():
        dc = DutClients(dut, dcon[dut]['ip'], '22', 'admin', 'broadcom')
        g_dut_clients[dcon[dut]['ip']] = dc

    if tc_name:
        wl_file = tc_name
        read_commands_from_file(wl_file)
        run_commands(wl_file)
        return

    with open(test_suite_name, 'r') as wl_suite:
        for wl_file in wl_suite.readlines():
            wl_file = wl_file.strip()
            if wl_file == '':
                continue

            read_commands_from_file(wl_file)
            run_commands(wl_file)

    pass


def run_commands(wl_file) -> None:
    """
    Run automation from watch_list
    :return:
    """
    r_syslog('INFO', '#########################################')
    r_syslog('INFO', 'RUN Commands from {}'.format(wl_file[:-5]))
    r_syslog('INFO', '#########################################')

    for dut_cmdno, val in g_wl_dict.items():
        dut = dut_cmdno.split('-')[0]
        dut_ip = dcon[dut]['ip']
        dc = g_dut_clients[dut_ip]
        cmd: str = val['cmd']
        watchers: typing.List = val['watchers']

        watchers = json.loads(utils.replace_variables_to_dut_port_name(dut, json.dumps(watchers)))
        cmd      = utils.replace_variables_to_dut_port_name(dut, cmd)
        r_syslog('INFO', '{} : executing : {}'.format(dut_cmdno, cmd))

        dc.exec_cmd(dut_cmdno, cmd, watchers)

    pass
