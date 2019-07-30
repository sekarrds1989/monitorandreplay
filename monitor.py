import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import copy
import textfsm
from tabulate import tabulate
import json
import glob
import re
import fcntl
import argparse

fptr = None
g_exec_mode = False


def process_show_output(cmd, stdout):
    stdout_data = stdout.read()
    cmd_file = cmd[5:].replace(' ', '_')
    try:
        re_table = None
        for f in glob.glob('templates/*.tmpl'):
            if cmd_file in f:
                template = open(f)
                re_table = textfsm.TextFSM(template)
                template.close()
        if not re_table:
            raise Exception('template file not found for {}'.format(cmd_file))

        fsm_results = re_table.ParseText(stdout_data)
        print(tabulate(fsm_results, headers=re_table.header, showindex='always', tablefmt='psql'))
    except Exception as e:
        print('Template parsing Failed')
        print('Received exception : {}'.format(e))
        print(stdout_data)
        return None
    return re_table, fsm_results


def read_int_in_range(prefix_str, min_int, max_int):
    while True:
        try:
            val = int(raw_input(prefix_str))
            if min_int <= val <= max_int:
                return val
        except Exception as e:
            print('Please enter a valid int in range {}-{}'.format(min_int, max_int))
            print('Received exception : {}'.format(e))
            continue
    pass


class DutListener:
    def __init__(self, hostname, port, uname, pwd):
        self.pwd = pwd
        self.uname = uname
        self.port = port
        self.hostname = hostname
        self.client = pc.SSHClient()
        self.g_cmd_no = 0
        try:
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(self.hostname, username=self.uname, password=self.pwd)
        except Exception as e:
            print('Client connection Failed : {} {} {} {}'.format(hostname, port, uname, pwd))
            print('Recieved exception : {}'.format(e))
            self.client.close()
            sys.exit(1)

    def add_to_watch_list(self, cmd, val=None):
        if g_exec_mode:
            return

        global fptr
        self.g_cmd_no += 1
        p_dict = {self.hostname: {'cmd_no': self.g_cmd_no, 'cmd': cmd, 'watch_list': val}}
        fcntl.flock(fptr, fcntl.LOCK_EX)
        json.dump(p_dict, fptr, sort_keys=True, indent=4)
        fcntl.flock(fptr, fcntl.LOCK_UN)
        fptr.flush()
        pass

    def launch_terminal(self):
        print ('launching terminal')
        while True:
            cmd = raw_input('cmd>> ')
            if cmd in ['q', 'exit', 'quit']:
                break
            if cmd in ['h', 'help', '?']:
                print('Enter "exit/quit/q" stop this session.')
                continue

            if cmd.startswith('sleep'):
                r1 = re.match(r'sleep ([\d]+)', cmd)
                if r1:
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
                            print('{}'.format(line.strip()))
                        continue
                except Exception as e:
                    print('Command execution Failed')
                    print('Received exception : {}'.format(e))
                    break

                if cmd.startswith('sudo config'):
                    self.add_to_watch_list(cmd)
                else:  # cmd.startswith('sudo show'):
                    ret = process_show_output(cmd, stdout)
                    if ret is None:
                        continue
                    else:
                        re_table, fsm_results = ret

                    # ignore further processing in exec-oly mode
                    if g_exec_mode:
                        continue

                    print('Add watchers.')
                    watch_list = []
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
                                col = raw_input('watch>> col : ')
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
                        watch_list.append(temp_dict)
                    self.add_to_watch_list(cmd, val=watch_list)
                    pass  # End of while True
        # End of while True
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DUT Listener options.')
    parser.add_argument('-e', '--exec_mode',action="store_true", default=False, help='Commands collection will not be done')
    parser.add_argument('ip', help='dut ip')
    parser.set_defaults(exec_mode=False)
    args = parser.parse_args()

    g_exec_mode = args.exec_mode

    try:
        fptr = open('watch_list.json', "a+")
    except Exception as e:
        print('failed to open watch_list file')
        print('Exception : {}'.format(e))
        sys.exit(1)

    dut = DutListener(sys.argv[1], '22', 'admin', 'broadcom')
    dut.launch_terminal()
    pass
