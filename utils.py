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

g_pdb_set = False

empty_tuple: tp.Tuple = ()
sudo_offset: int = len('sudo ')

show_cmd_pattern = ('sudo udldctl',
                    'sudo show')
prompt_options = ('sonic#', ':~$')

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
            log_excp('Exception : {}'.format(e))
            break

    return resp


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

    if cmd.startswith('udldctl port'):
        cmd_file = 'udldctl_port.tmpl'
    else:
        cmd = cmd[sudo_offset:]
        cmd_file = cmd.replace(' ', '_')

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
        log_info(tabulate(fsm_results, headers=re_table.header, showindex='always', tablefmt='psql'))
    except Exception as e:
        log_err('Template parsing Failed')
        log_err('Received exception : {}'.format(e))
        log_err(stdout)
        return ()
    return re_table, fsm_results


# Create a custom logger
mr_log: logging.Logger = logging.getLogger(__name__)


def logger_init():

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler    = logging.FileHandler('logs/mrlog.log')

    console_handler.setLevel(logging.DEBUG) # change to appropriate level after dev complete
    file_handler.setLevel(logging.INFO) # change it to appropriate level

    # Create formatter and add it to handlers
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    mr_log.addHandler(console_handler)
    mr_log.addHandler(file_handler)
    mr_log.setLevel(logging.DEBUG)

    """
    this is for root logger. if we didnt create separate mr_log.
    logging.basicConfig(level=logging.DEBUG
                        , format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                        , handlers=[console_handler, file_handler])
    """


def log_debug(msg: str) -> None:
    mr_log.debug(msg)


def log_info(msg: str) -> None:
    mr_log.info(msg)


def log_err(msg: str) -> None:
    if g_pdb_set:
        pdb.set_trace()
    mr_log.error(msg)


def log_excp(msg: str) -> None:
    if g_pdb_set:
        pdb.set_trace()
    mr_log.exception(msg)
