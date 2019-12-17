"""
utils.py::
This file holds utility functions used across this project. viz. logger and output parsing.
"""

import glob
import logging
import typing as tp
import pdb
import textfsm
from tabulate import tabulate
import time
import re
import os
import copy
import json
import fcntl
import shutil
from datetime import datetime
import sys

from topo import dut_ports


# Create a custom logger
monitor_logger: logging.Logger = logging.getLogger(__name__)
replay_logger: logging.Logger = logging.getLogger(__name__)

g_pdb_set = False

empty_tuple: tp.Tuple = ()
sudo_offset: int = len('sudo ')

show_cmd_pattern = ('sudo udldctl',
                    'sudo show')
prompt_options = ('sonic#', ':~$')
g_runtime_variables = './rt_vars.txt'


def create_rt_vars_file(file_comment='Vars for testsuite ABC'):
    if os.stat(g_runtime_variables).st_size != 0:
        try:
            shutil.copy(g_runtime_variables, g_runtime_variables + datetime.now().__str__().replace(' ', '_'))
        except IOError as e:
            print("Unable to copy file. {}".format(e))
        except Exception as e:
            print("Unexpected error: ", sys.exc_info())

    line = '{'+'\n    "comment": "{}"\n'.format(file_comment)
    with open(g_runtime_variables, 'w') as f:
        f.writelines(line)


def monitor_logger_init():
    open('logs/monitor.log', 'w').close()

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler    = logging.FileHandler('logs/monitor.log')

    console_handler.setLevel(logging.DEBUG)  # change to appropriate level after dev complete
    file_handler.setLevel(logging.DEBUG)  # change it to appropriate level

    # Create formatter and add it to handlers
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    monitor_logger.addHandler(console_handler)
    monitor_logger.addHandler(file_handler)
    monitor_logger.setLevel(logging.DEBUG)


def replay_logger_init():
    open('logs/replay.log', 'w').close()

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler    = logging.FileHandler('logs/replay.log')

    console_handler.setLevel(logging.DEBUG)  # change to appropriate level after dev complete
    file_handler.setLevel(logging.DEBUG)  # change it to appropriate level

    # Create formatter and add it to handlers
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    replay_logger.addHandler(console_handler)
    replay_logger.addHandler(file_handler)
    replay_logger.setLevel(logging.DEBUG)

    """
    this is for root logger. if we didnt create separate monitor_logger.
    logging.basicConfig(level=logging.DEBUG
                        , format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                        , handlers=[console_handler, file_handler])
    """


def m_log_debug(msg: str) -> None:
    monitor_logger.debug(msg)


def m_log_info(msg: str) -> None:
    monitor_logger.info(msg)


def m_log_err(msg: str) -> None:
    if g_pdb_set:
        pdb.set_trace()
    monitor_logger.error(msg)


def m_log_excp(msg: str) -> None:
    monitor_logger.exception(msg)


def r_log_debug(msg: str) -> None:
    replay_logger.debug(msg)


def r_log_info(msg: str) -> None:
    replay_logger.info(msg)


def r_log_err(msg: str) -> None:
    if g_pdb_set:
        pdb.set_trace()
    replay_logger.error(msg)


def r_log_excp(msg: str) -> None:
    if g_pdb_set:
        pdb.set_trace()
    replay_logger.exception(msg)


def get_file_name(tc_name: str):
    if tc_name.find('watch_lists/') == -1:
        return 'watch_lists/'+tc_name+'.json'
    return tc_name+'.json'


def read_int_in_range(prefix_str, min_int, max_int) -> int:
    """
    Read a number from terminal

    :param prefix_str: information printed to user
    :param min_int: range start
    :param max_int: range end
    :return: number
    """
    while True:
        try:
            val = int(input(prefix_str))
            if min_int <= val <= max_int:
                return val
        except Exception as e:
            m_log_excp('Please enter a valid int in range {}-{}'.format(min_int, max_int))
            m_log_excp('Received exception : {}'.format(e))
            continue
    pass


def replace_variables_to_dut_port_name(dut, str_t):
    """

    :param dut:
    :param str_t:
    :return:

    sort dut_ports[dut] by max key length to avoid substring overwrite problem
    ex:
    For 'D1': {'P1': 'Ethernet26', 'P1_1': 'Ethernet 26'},
    D1P1 and D1P1_1 are the variable names.
    when we search and replace in below given output it replaces interface D1P1_1 -> interface Ethernet26_1
        "D2-1": {
        "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface D1P1_1\" -c \"no shutdown\"",
        "watchers": []
    }

    2019-12-12 14:54:17,367 - utils - INFO - D1-1 : executing : sudo sonic-cli -c "configure terminal" -c "interface Ethernet26_1" -c "no shutdown"

    So sort by longest key length at 1st index.

    """

    p_dict = copy.deepcopy(dut_ports[dut])
    # sorted(p_dict.items(), key=lambda s: len(s[0]), reverse=True)
    # we can also reverse sort them by length of key, but i believe just reverse should also do the trick.
    p_dict = dict(sorted(p_dict.items(), reverse=True))
    if str_t:
        for port in p_dict.keys():
            str_t = str_t.replace(dut + port, p_dict[port])
    return str_t


def replace_dut_port_names_to_variables(dut, str_t):
    if str_t:
        for port in dut_ports[dut].keys():
            str_t = str_t.replace(dut_ports[dut][port], dut + port)
    return str_t


def run_command(chan, cmd, wait_time=10):
    chan.send(cmd + '\n')

    # give sufficient time for command to execute and populate stdout.
    # else recv will return nothing in this call.
    # and data will be processed only in next call.
    time.sleep(1)

    buff_size = -1
    resp = ''
    while not resp.strip().endswith(prompt_options):
        try:
            chan.settimeout(wait_time)
            buff = chan.recv(buff_size).decode()
            resp += buff
        except Exception as e:
            m_log_excp('Exception : {}'.format(e))
            break

    return resp


def find_template_name_for_cmd(cmd):
    cmd = cmd.strip()
    if cmd.startswith('sudo '):
        cmd = cmd[len('sudo '):]

    match_tmpl = ''
    with open('cmd_template_map.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue

            p_cmd = line.split('->')[0].strip()

            if re.match(p_cmd, cmd):
                match_tmpl = line.split('->')[1].strip()
                break

    if not match_tmpl:
        m_log_debug('Template not found for cmd : {}'.format(cmd))
    else:
        m_log_debug('Cmd : {} => Template : {}'.format(p_cmd, match_tmpl))

    return match_tmpl


def process_show_output(cmd: str, stdout) -> tp.Tuple:
    """
    Execute the given 'cmd' and process the show output from stdout
    :param cmd: command to be executed on stdout
    :param stdout:
    :return:
     on error   -   None
     on success -   re_table, fsm_results

     re_table   : tabular format of template
     fsm_results: parsed output

    """

    cmd_file = find_template_name_for_cmd(cmd)
    if not cmd_file:
        m_log_debug('\n {}'.format(stdout))
        return -1, -1

    try:
        re_table = None
        for f in glob.glob('./templates/*.tmpl'):
            if cmd_file in f:
                template = open(f)
                re_table = textfsm.TextFSM(template)
                template.close()
        if not re_table:
            raise Exception('template file not found for {}'.format(cmd_file))

        fsm_results = re_table.ParseText(stdout)
        m_log_info('\n' + tabulate(fsm_results, headers=re_table.header, showindex='always', tablefmt='psql'))
    except Exception as e:
        m_log_err('Template parsing Failed')
        m_log_err('Received exception : {}'.format(e))
        m_log_err(stdout)
        return -1, -1
    return re_table, fsm_results


def add_runtime_variables(header, data, nrows, ncols):
    if nrows <= 0 or ncols <= 0:
        return

    new_vars = {}
    while True:
        var_name = input('variable name : ')
        if var_name == 'end':
            break

        var_name = 'MR_RT_VAR_' + var_name

        vars_str = ' '
        with open(g_runtime_variables, 'r') as f:
            lines = f.readlines()
            lines.append('}')
            curr_var_dict = json.loads(vars_str.join(lines))

        if var_name in curr_var_dict.keys():
            m_log_err('Variable name already exists, Enter new name')
            continue

        m_log_info('Variable is located @')
        row  = read_int_in_range('row : ', 0, nrows)
        col  = read_int_in_range('col : ', 0, ncols)

        col_name = header[col]

        import pdb
        pdb.set_trace()
        var_value = data[row][col]
        var_map_dict = {var_name: var_value}
        new_vars[str(row)+'_'+col_name] = var_name
        p_data = json.dumps(var_map_dict, indent=4)
        p_data = ',' + p_data[2:-1]

        with open(g_runtime_variables, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.writelines(p_data)
            fcntl.flock(f, fcntl.LOCK_UN)

        data[row][col] = var_name

    return data, new_vars

