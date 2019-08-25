import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import copy
import json
import re
import fcntl
import utils as utils

g_exec_mode = False


def read_int_in_range(prefix_str, min_int, max_int):
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
    def __init__(self, hostname, port, uname, pwd, exec_mode=False):
        self.pwd = pwd
        self.uname = uname
        self.port = port
        self.hostname = hostname
        self.client = pc.SSHClient()
        self.exec_mode = exec_mode
        self.g_cmd_no = 0
        try:
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(self.hostname, username=self.uname, password=self.pwd)
        except Exception as e:
            utils.log_excp('Client connection Failed : {} {} {} {}'.format(hostname, port, uname, pwd))
            utils.log_excp('Received exception : {}'.format(e))
            self.client.close()
            sys.exit(1)

        try:
            self.wl_fd = open('watch_list.json', "w")
        except Exception as e:
            utils.log_dbg('failed to open watch_list file')
            utils.log_err('Exception : {}'.format(e))
            sys.exit(1)

    def add_to_watch_list(self, cmd, val=None):
        if g_exec_mode:
            return

        self.g_cmd_no += 1
        p_dict = {self.hostname: {'cmd_no': self.g_cmd_no, 'cmd': cmd, 'watchers': val}}
        fcntl.flock(self.wl_fd, fcntl.LOCK_EX)
        json.dump(p_dict, self.wl_fd, sort_keys=True, indent=4)
        fcntl.flock(self.wl_fd, fcntl.LOCK_UN)
        self.wl_fd.flush()
        pass

    def launch_terminal(self):
        if self.exec_mode:
            self.launch_exec_only_terminal()
        else:
            self.launch_monitor_terminal()

    def launch_exec_only_terminal(self):
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

    def launch_monitor_terminal(self):
        while True:
            cmd = input('cmd>> ')
            if cmd in ['q', 'exit', 'quit']:
                break
            elif cmd in ['h', 'help', '?']:
                print('Enter "exit/quit/q" stop this session.')
            elif cmd.startswith('sleep'):
                r1 = re.match(r"sleep [.]?([\d]+)", cmd)
                if not r1:
                    print('Provide a valid value to sleep, refer time.sleep')
                else:
                    self.add_to_watch_list(cmd)
            elif cmd.startswith(('config', 'show', 'sudo config')):
                # prepend sudo if its not there already
                if cmd.startswith('config'):
                    cmd = 'sudo ' + cmd

                try:
                    stdin, stdout, stderr = self.client.exec_command(cmd)
                    lines = stderr.readlines()
                    if len(lines):
                        for line in lines:
                            utils.log_dbg('{}'.format(line.strip()))
                        continue
                except Exception as e:
                    utils.log_excp('Command execution Failed')
                    utils.log_excp('Received exception : {}'.format(e))
                    break

                if cmd.startswith('sudo config'):
                    self.add_to_watch_list(cmd)
                else:  # cmd.startswith('sudo show'):
                    ret = utils.process_show_output(cmd, stdout)
                    if ret is None:
                        continue
                    else:
                        re_table, fsm_results = ret

                    utils.log_info('Add watchers.')
                    watchers = []
                    while True:
                        row = read_int_in_range('watch>> row : ', min_int=-1, max_int=len(fsm_results)-1)
                        if row == -1:
                            break
                        row_dict = dict(zip(re_table.header, fsm_results[row]))

                        print('select columns watch mode')
                        print('all          : 0')
                        print('ignore list  : 1')
                        print('include list : 2')
                        mode = read_int_in_range('mode : ', min_int=0, max_int=2)

                        if mode != 0:
                            user_dict = {}
                            while True:
                                col = input('watch>> col : ')
                                if col == 'end':
                                    break
                                if col not in re_table.header:
                                    print('Invalid input : {}'.format(col))
                                    print('Enter "end" to exit')
                                    continue

                                user_dict[col] = row_dict[col]
                            # End of while

                            if mode == 1:
                                temp_dict = dict(set(row_dict.items()) - set(user_dict.items()))
                            else:
                                temp_dict = copy.deepcopy(user_dict)
                        else:
                            temp_dict = copy.deepcopy(row_dict)
                        watchers.append(temp_dict)
                    self.add_to_watch_list(cmd, val=watchers)
                    pass  # End of while True
            else:
                # all valid command processing is complete
                # anything else is a invalid command
                print('invalid command')
        # End of while True
    pass


