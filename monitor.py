import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import copy
import json
import re
import fcntl
import utils as utils

fptr = None
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

    def add_to_watch_list(self, cmd, val=None):
        if g_exec_mode:
            return

        global fptr
        self.g_cmd_no += 1
        p_dict = {self.hostname: {'cmd_no': self.g_cmd_no, 'cmd': cmd, 'watchers': val}}
        fcntl.flock(fptr, fcntl.LOCK_EX)
        json.dump(p_dict, fptr, sort_keys=True, indent=4)
        fcntl.flock(fptr, fcntl.LOCK_UN)
        fptr.flush()
        pass

    def launch_terminal(self):
        utils.log_info('launching terminal')
        while True:
            cmd = input('cmd>> ')
            if cmd in ['q', 'exit', 'quit']:
                break
            if cmd in ['h', 'help', '?']:
                print('Enter "exit/quit/q" stop this session.')
                continue

            if cmd.startswith('sleep'):
                r1 = re.match(r'sleep [.]?([\d]+)', cmd)
                if not r1:
                    print('Provide a valid value to sleep, refer time.sleep')
                    continue
                self.add_to_watch_list(cmd)
                continue

            if cmd.startswith(('config', 'show')):
                cmd = 'sudo ' + cmd
            if cmd.startswith(('sudo config', 'sudo show')):
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

                    # ignore further processing in exec-oly mode
                    if self.exec_mode:
                        continue

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
            # all valid command processing is complete
            # anything else is a invalid command
            utils.log_err('invalid command')
        # End of while True
    pass


