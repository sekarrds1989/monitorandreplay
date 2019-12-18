import typing
import re
from time import sleep
import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import json
import datetime
from tabulate import tabulate
import utils as utils
from topo import dut_connections as dcon
import topo

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
"""
ssh client object dictionary
each dut will have a client obj
"""
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
        self.log_file = open(topo.logs_dir + dut_name + '.log', 'w')

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

    def exec_cmd(self, tc_id, cmd, exp_op_list, create_rt_vars):
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

            if create_rt_vars and len(create_rt_vars.keys()) != 0:
                for key in create_rt_vars.keys():
                    row, col = create_rt_vars[key]
                    utils.add_new_rt_var_into_file(key, fsm_results[row][col], True)

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
                            try:
                                diff_table[0].append(exp_op[key])
                            except KeyError:
                                diff_table[0].append('')
                            diff_table[1].append(p_dict[key])
                        self.syslog('ERR', ' Exp Vs Actual \n {}'.format(tabulate(diff_table, headers=header
                                                                                  , showindex='always'
                                                                                  , tablefmt='psql')))
                    self.syslog('ERR', 'Test {} FAILED'.format(tc_id))
                    self.abort_test()

            self.syslog('INFO', 'Test {} PASSED'.format(tc_id))
        pass


def start_automation(test_suite_name, tc_name='') -> None:
    """
    Read watch_list file and create all required ssh sessions.

    :return: None
    """
    for dut in dcon.keys():
        dc = DutClients(dut, dcon[dut]['ip'], '22', 'admin', 'broadcom')
        g_dut_clients[dcon[dut]['ip']] = dc

    if tc_name:
        wl_file = tc_name
        wl_dict = utils.read_json_file_as_dict(wl_file)
        if wl_dict is not None:
            process_commands(wl_file, wl_dict)
    else:
        with open(test_suite_name, 'r') as wl_suite:
            for wl_file in wl_suite.readlines():
                wl_file = wl_file.strip()
                if wl_file == '' or wl_file.startswith('#'):
                    continue

                wl_dict = utils.read_json_file_as_dict(wl_file)
                if wl_dict is not None:
                    process_commands(wl_file, wl_dict)
    pass


def process_commands(wl_file, wl_dict) -> None:
    """
    Run automation from watch_list
    :return:
    """
    r_syslog('INFO', '#########################################')
    r_syslog('INFO', 'RUN Commands from {}'.format(wl_file))
    r_syslog('INFO', '#########################################')

    rt_vars = utils.read_json_file_as_dict(utils.g_runtime_variables)

    for dut_cmd_no, w_val in wl_dict.items():
        dut = dut_cmd_no.split('-')[0]
        dut_ip = dcon[dut]['ip']
        dc = g_dut_clients[dut_ip]
        cmd: str = w_val['cmd']
        watchers: typing.List = w_val['watchers']
        create_rt_vars: typing.Dict = w_val['rt_vars']

        if len(watchers) > 1:
            p_dict = watchers[1]

            for key, val in watchers[1].items():
                if val.startswith('MR_RT_VAR_'):
                    if val not in rt_vars.keys():
                        r_syslog('ERR', 'missing run time variable {} in rt_vars'.format(val))
                        sys.exit(-1)
                    else:
                        p_dict[key] = rt_vars[val]

        watchers = json.loads(utils.replace_variables_to_dut_port_name(dut, json.dumps(watchers)))
        cmd      = utils.replace_variables_to_dut_port_name(dut, cmd)
        r_syslog('INFO', '{} : executing : {}'.format(dut_cmd_no, cmd))

        dc.exec_cmd(dut_cmd_no, cmd, watchers, create_rt_vars)

    pass


def idp_start_automation():
    """
    Read watch_list file and create all required ssh sessions.

    :return: None
    """
    for dut in dcon.keys():
        dc = DutClients(dut, dcon[dut]['ip'], '22', 'admin', 'broadcom')
        g_dut_clients[dcon[dut]['ip']] = dc
    pass
