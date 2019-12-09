import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import copy
import json
import re
import fcntl
import utils as utils
import typing as tp
import os

from topo import dut_connections as dcon

show_cmd_pattern = ('udldctl',
                    'sudo show',
                    'show')

g_exec_only_mode = False
g_check_wl_status = True


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
            utils.log_excp('Please enter a valid int in range {}-{}'.format(min_int, max_int))
            utils.log_excp('Received exception : {}'.format(e))
            continue
    pass


class DutListener:
    """
    This Class will Listen to all actions happening on the DUT.
    Will launch a terminal for the user.
    Any thing that happens on this terminal is recorded in a file.
    """

    def __init__(self, hostip: str, port: str, uname: str, pwd: str, exec_only_mode: bool = False):
        """
        1) Create a connection to given hostip:port with specified uname & pwd.
        2) open watch_list.json file in append mode. there might be more than on DutListeners in action.

        :param hostip:
        :param port: 
        :param uname: 
        :param pwd: 
        :param exec_only_mode: 
         True: Dont capture the actions on this terminal
         False: Capture the actions on this terminal 
        """
        self.pwd = pwd
        self.uname = uname
        self.port = port
        self.hostip = hostip
        self.client = pc.SSHClient()
        self.exec_only_mode = exec_only_mode
        self.g_cmd_no = 0
        self.hostname = 'NA'

        for dut in dcon.keys():
            if dcon[dut]['ip'] == hostip:
                self.hostname = dut

        try:
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(self.hostip, username=self.uname, password=self.pwd)
        except Exception as e:
            utils.log_excp('Client connection Failed : {} {} {} {}'.format(hostip, port, uname, pwd))
            utils.log_excp('Received exception : {}'.format(e))
            self.client.close()
            sys.exit(1)

        try:
            self.wl_fd = open('watch_list.json', "a")

        except Exception as e:
            utils.log_dbg('failed to open watch_list file')
            utils.log_err('Exception : {}'.format(e))
            sys.exit(1)

        pass

    def add_to_watch_list(self, cmd: str, val: tp.List = None) -> None:
        """
         create a watch_list template.
         convert it to json format and append to watch_list file.
        :param cmd: command string
        :param val: list of dictionary containing which variable to be watched.
        :return:
        """
        if g_exec_only_mode:
            return

        self.g_cmd_no += 1
        # fmi, json doesnt accept keys in tuple format.
        p_dict = {self.hostname + '-' + str(self.g_cmd_no): {'cmd': cmd, 'watchers': val}}
        data = json.dumps(p_dict, sort_keys=True, indent=4)

        fcntl.flock(self.wl_fd, fcntl.LOCK_EX)
        global g_check_wl_status
        if g_check_wl_status:
            g_check_wl_status = False
            if os.stat("watch_list.json").st_size == 0:
                data = '{\n' + data[1:len(data) - 1]
            else:
                data = ',' + data[1:len(data) - 1]
        else:
            data = ',' + data[1:len(data) - 1]

        self.wl_fd.writelines(data)
        fcntl.flock(self.wl_fd, fcntl.LOCK_UN)

        self.wl_fd.flush()
        pass

    def launch_terminal(self):
        if self.exec_only_mode:
            self.launch_exec_only_terminal()
        else:
            self.launch_monitor_terminal()

    def launch_exec_only_terminal(self) -> None:
        """
        Launch a execute only terminal.
        No action on this terminal will be captured in watch_list file.
        :return: None
        """
        while True:
            cmd = input('cmd>> ')
            if cmd in ['q', 'exit', 'quit']:
                self.wl_fd.close()
                break
            if cmd in ['h', 'help', '?']:
                print('Enter "exit/quit/q" stop this session.')
                continue

            if cmd.startswith(('config', 'show')):
                cmd = 'sudo ' + cmd
            if cmd.startswith(('sudo config', 'sudo show')):
                try:
                    stdin, stdout, stderr = self.client.exec_command(cmd)
                    lines = stderr.readlines()
                    if len(lines):
                        for line in lines:
                            print('{}'.format(line.strip()))
                        continue
                    lines = stdout.readlines()
                    if len(lines):
                        for line in lines:
                            print('{}'.format(line.strip()))
                        continue
                except Exception as e:
                    utils.log_excp('Command execution Failed')
                    utils.log_excp('Received exception : {}'.format(e))
                    break

    def launch_monitor_terminal(self) -> None:
        """
        Launch a terminal and capture all actions happening on this terminal.
        we will create a watch_list file to generate automation script.
        :return: None
        """
        while True:
            cmd = input('sonic# ')
            if cmd in ['q', 'exit', 'quit']:
                break
            elif cmd in ['h', 'help', '?']:
                print('Enter "exit/quit/q" stop this session.')
                continue
            elif cmd.startswith('sleep'):
                r1 = re.match(r'sleep [.]?([\d]+)', cmd)
                if not r1:
                    print('Provide a valid value to sleep, refer time.sleep')
                    continue
            else:
                try:
                    stdin, stdout, stderr = self.client.exec_command(cmd)

                    lines = stderr.readlines()
                    if len(lines):
                        for line in lines:
                            utils.log_err('{}'.format(line.strip()))
                        continue
                except Exception as e:
                    utils.log_excp('Command execution Failed')
                    utils.log_excp('Received exception : {}'.format(e))
                    break

                #print(stdout.readlines())

                if cmd.startswith(show_cmd_pattern):
                    ret = utils.process_show_output(cmd, stdout)
                    if ret is None:
                        continue
                    else:
                        re_table, fsm_results = ret

                    utils.log_info('Add watchers.')
                    watchers = None
                    while True:
                        watch_str = input('watch>> (row_list:col_list) : ')
                        if watch_str == 'end':
                            break
                        elif watch_str.count(':') != 1:
                            print('%Error% Invalid Input')
                            print('FORMAT ->> row-index-list:col-index-list')
                            print('\'end\' to stop')
                            print('ex:')
                            print('1,2,3::4 >> watch 4th column in rows 1,2,3')
                            print('1,2,3::-1 >> watch all columns in rows 1,2,3')
                            print('-1::4 >> watch 4th column in all rows')
                            continue

                        row_str, col_str = tuple(watch_str.split(':'))
                        if row_str == '-1':
                            row_list = list(range(0, len(fsm_results)))
                        else:
                            row_list = re.findall("[\d]+", row_str)
                            row_list = list(map(int, row_list))

                        if col_str == '-1':
                            col_list = list(range(0, len(re_table.header)))
                        else:
                            col_list = re.findall("[\d]+", col_str)
                            col_list = list(map(int, col_list))

                        for row in row_list:
                            if row >= len(fsm_results):
                                continue
                            row_dict = dict(zip(re_table.header, fsm_results[row]))
                            user_dict = {}
                            for col in col_list:
                                if col >= len(re_table.header):
                                    continue
                                col_name = re_table.header[col]
                                user_dict[col_name] = row_dict[col_name]
                            # end for col in col_list:
                            watchers.append(user_dict)
                        # end for row in row_list
                    # end while True for watchlist
                else:
                    watchers = None
            self.add_to_watch_list(cmd, val=watchers)
        # End of while True
    pass
