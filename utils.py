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

g_pdb_set = False

empty_tuple: tp.Tuple = ()
sudo_offset: int = len('sudo ')

show_cmd_pattern = ('sudo udldctl',
                    'sudo show')
prompt_options = ('sonic#', ':~$')


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


# Create a custom logger
monitor_logger: logging.Logger = logging.getLogger(__name__)
replay_logger: logging.Logger = logging.getLogger(__name__)


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