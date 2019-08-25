import glob
import logging
from typing import Dict, Any
import pdb
import textfsm
from tabulate import tabulate

g_pdb_set = False


def process_show_output(cmd, stdout):
    stdout_data = stdout.read().decode('utf-8')
    cmd_file = cmd[5:].replace(' ', '_')
    try:
        re_table = None
        for f in glob.glob('./templates/*.tmpl'):
            if cmd_file in f:
                template = open(f)
                re_table = textfsm.TextFSM(template)
                template.close()
        if not re_table:
            raise Exception('template file not found for {}'.format(cmd_file))

        fsm_results = re_table.ParseText(stdout_data)
        print(tabulate(fsm_results, headers=re_table.header, showindex='always', tablefmt='psql'))
    except Exception as e:
        log_err('Template parsing Failed')
        log_err('Received exception : {}'.format(e))
        log_err(stdout_data)
        return None
    return re_table, fsm_results


# Create a custom logger
mr_log: logging.Logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('logs/mrlog.log')

c_handler.setLevel(logging.DEBUG) # change to appropriate level after dev complete
c_handler.setLevel(logging.INFO) # change to appropriate level after dev complete
c_handler.setLevel(logging.ERROR) # change to appropriate level after dev complete

f_handler.setLevel(logging.INFO) # change it to appropriate level
f_handler.setLevel(logging.ERROR) # change it to appropriate level

# Create formatter and add it to handlers
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
mr_log.addHandler(c_handler)
mr_log.addHandler(f_handler)


def log_dbg(msg: str) -> None:
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
