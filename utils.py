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
import difflib

from topo import dut_ports
import topo


# Create a custom logger
monitor_logger: logging.Logger = logging.getLogger(__name__)
replay_logger: logging.Logger = logging.getLogger(__name__)

g_pdb_set = False

empty_tuple: tp.Tuple = ()
sudo_offset: int = len('sudo ')

show_cmd_pattern = ('sudo udldctl',
                    'sudo show')
prompt_options = ('sonic#', ':~$')
g_runtime_variables = topo.g_rt_vars_file


def backup_rt_vars_file(file_name):
    if os._exists(file_name) and os.stat(file_name).st_size != 0:
        try:
            shutil.copy(file_name, file_name + datetime.now().__str__().replace(' ', '_'))
        except IOError as e:
            print("Unable to copy file. {}".format(e))
        except Exception as e:
            print("Unexpected error: ", sys.exc_info())


def create_rt_vars_file():
    backup_rt_vars_file(g_runtime_variables)
    open(g_runtime_variables, 'w').close()
    """
    line = '{'+'\n    "comment": "{}"\n'.format(file_comment)
    with open(g_runtime_variables, 'w') as f:
        f.writelines(line)
    """


def monitor_logger_init():
    open(topo.logs_dir+'monitor.log', 'w').close()

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler    = logging.FileHandler(topo.logs_dir+'monitor.log')

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
    open(topo.logs_dir+'replay.log', 'w').close()

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler    = logging.FileHandler(topo.logs_dir+'replay.log')

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
    if tc_name.find(topo.wl_dir) == -1:
        return topo.wl_dir+tc_name+'.json'
    return tc_name+'.json'


def get_max_cmd_no(f_name, dut_name):
    p_dict = read_json_file_as_dict(f_name)
    if p_dict is None or len(p_dict.keys()) == 0:
        return 0

    max_cmd_no = -1
    for key in p_dict.keys():
        if key.startswith(dut_name):
            cmd_no = int(key[len(dut_name+'-'):])
            if cmd_no > max_cmd_no:
                max_cmd_no = cmd_no

    return max_cmd_no


def read_json_file_as_dict(wl_file):
    """
    r_log_info('Read commands from : {}'.format(wl_file))
    wl = open(wl_file, 'r')
    try:
        p_dict = json.load(wl)
    except Exception:
        wl.close()
        r_log_err('File Not in proper JSON format, append } at end')
        with open(wl_file, 'a') as f:
            f.writelines('}')
            f.close()

        try:
            with open(wl_file, 'r') as wl:
                p_dict = json.load(wl)
        except Exception:
            r_log_err('failed to read {}'.format(wl_file))
            p_dict = None

    """
    # r_log_info('Read commands from : {}'.format(wl_file))
    if os.stat(wl_file).st_size == 0:
        return {}

    with open(wl_file, 'r') as wl:
        try:
            p_dict = json.load(wl)
        except json.JSONDecodeError:
            p_dict = None
            r_log_err('File Not in proper JSON format')

    return p_dict




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
    with open(topo.cmd_to_template_map, 'r') as f:
        p_dict = json.load(f)
        for key in p_dict.keys():
            if re.match(key, cmd):
                match_tmpl = p_dict[key]
                break

    if not match_tmpl:
        m_log_debug('Template not found for cmd : {}'.format(cmd))
    else:
        m_log_debug('Cmd : {} => Template : {}'.format(cmd, match_tmpl))

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
        for f in glob.glob(topo.templates_dir+'*.tmpl'):
            if cmd_file in f:
                template = open(f)
                re_table = textfsm.TextFSM(template)
                template.close()
        if not re_table:
            raise Exception('template file not found for {}'.format(cmd_file))

        fsm_results = re_table.ParseText(stdout)
        header = ['({}) '.format(col_id)+col_name for col_id, col_name in enumerate(re_table.header)]
        m_log_info('\n' + tabulate(fsm_results, headers=header, showindex='always', tablefmt='psql'))
    except Exception as e:
        m_log_err('Template parsing Failed')
        m_log_err('Received exception : {}'.format(e))
        m_log_err(stdout)
        return -1, -1
    return re_table, fsm_results


def add_new_rt_var_into_file(var_name, var_value, in_replay_ctx):
    curr_var_dict = read_json_file_as_dict(g_runtime_variables)

    if not in_replay_ctx:
        if var_name in curr_var_dict.keys():
            print('Variable name already exists, Enter new name')
            if 'y' != input('do you want to overwrite it? [y/n]'):
                return

    curr_var_dict[var_name] = var_value
    with open(g_runtime_variables, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(curr_var_dict, f, indent=4)
        fcntl.flock(f, fcntl.LOCK_UN)
    m_log_info('Created variable {} = {}'.format(var_name, var_value))


def create_rt_vars_from_output(data, nrows, ncols):

    temp_data = copy.deepcopy(data)
    if nrows <= 0 or ncols <= 0:
        return

    rt_vars = {}
    while True:
        var_name = input('variable name : ')
        if var_name == 'end':
            break

        var_name = 'MR_RT_VAR_' + var_name

        m_log_info('Variable is located at')
        row  = read_int_in_range('row : ', 0, nrows)
        col  = read_int_in_range('col : ', 0, ncols)

        var_value = temp_data[row][col]

        add_new_rt_var_into_file(var_name, var_value, False)

        rt_vars[var_name] = (row, col)

    return rt_vars


def set_rt_vars_for_output(header, data, nrows, ncols):
    if nrows <= 0 or ncols <= 0:
        return

    # new_vars = {}
    while True:
        var_name = input('variable name [type "end" to stop] : ')
        if var_name == 'end':
            break

        var_name = 'MR_RT_VAR_' + var_name

        with open(g_runtime_variables, 'r') as f:
            try:
                curr_var_dict = json.load(f)
            except json.JSONDecodeError:
                print('File not in JSON format. \nfile data : {}'.format(f.readlines()))
                continue

        if var_name not in curr_var_dict.keys():
            print('Variable doesnt exist')
            print('closest possible matches : \n {}'.format(difflib.get_close_matches(var_name, curr_var_dict.keys())))
            continue

        m_log_info('Variable is located @')
        row  = read_int_in_range('row : ', 0, nrows)
        col  = read_int_in_range('col : ', 0, ncols)
        """
        col_name = header[col]

        var_value = data[row][col]
        var_map_dict = {var_name: var_value}
        new_vars[str(row)+'_'+col_name] = var_name
        p_data = json.dumps(var_map_dict, indent=4)
        p_data = ',' + p_data[2:-1]

        with open(g_runtime_variables, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            m_log_info('{}'.format(var_map_dict))
            f.writelines(p_data)
            fcntl.flock(f, fcntl.LOCK_UN)
        
        new_vars[str(row)+'_'+col_name] = var_name
        """
        data[row][col] = var_name

    return data

