import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import json
import re
import fcntl
import utils as utils
import typing as tp
import os

from topo import dut_connections as dcon
from topo import g_curr_tc_name_holder

class DutListener:
    """
    This Class will Listen to all actions happening on the DUT.
    Will launch a terminal for the user.
    Any thing that happens on this terminal is recorded in a file.
    """

    def __init__(self, hostip: str, test_suite: str, uname: str, pwd: str, exec_only_mode: bool = False):
        """
        1) Create a connection to given hostip:port with specified uname & pwd.
        2) open watch_list.json file in append mode. there might be more than on DutListeners in action.

        :param hostip:
        :param uname:
        :param pwd: 
        :param exec_only_mode: 
         True: Dont capture the actions on this terminal
         False: Capture the actions on this terminal 
        """
        self.pwd = pwd
        self.uname = uname
        self.port = '22'
        self.hostip = hostip
        self.client = pc.SSHClient()
        self.exec_only_mode = exec_only_mode
        self.g_cmd_no = 0
        self.dut_name = 'NA'
        self.wl_file_name = test_suite+'_init.json'
        self.test_suite = test_suite
        self.contd_count = 0

        for dut in dcon.keys():
            if dcon[dut]['ip'] == hostip:
                self.dut_name = dut

        try:
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(self.hostip, username=self.uname, password=self.pwd, timeout=10)
            transport = self.client.get_transport()
            self.chan = transport.open_session()
            self.chan.get_pty()
            self.chan.invoke_shell()

        except Exception as e:
            utils.m_log_excp('Client connection Failed : {} {} {} {}'.format(hostip, self.port, uname, pwd))
            utils.m_log_excp('Received exception : {}'.format(e))
            self.client.close()
            sys.exit(1)

        pass

    def create_new_watch_list_file(self, append_to_suite):
        self.g_cmd_no = 0
        self.contd_count = 0
        if append_to_suite:
            open(self.wl_file_name, "w").close()
            self.append_file_to_suite(self.wl_file_name)
            utils.m_log_info('TC: {} file flushed out'.format(self.wl_file_name))

    def add_cmd_to_curr_wl(self, cmd: str, val: tp.List = None) -> None:
        """
         create a watch_list template.
         convert it to json format and append to watch_list file.
        :param cmd: command string
        :param val: list of dictionary containing which variable to be watched.
        :return:
        """

        with open(g_curr_tc_name_holder, "rb") as f:
            tc_file_name = f.readline().strip().decode()

        if self.wl_file_name != tc_file_name:
            self.wl_file_name = tc_file_name
            self.create_new_watch_list_file(append_to_suite=False)

        self.g_cmd_no += 1

        cmd = utils.replace_dut_port_names_to_variables(self.dut_name, cmd)
        val = json.loads(utils.replace_dut_port_names_to_variables(self.dut_name, json.dumps(val)))

        p_dict = {self.dut_name + '-' + str(self.g_cmd_no): {'cmd': cmd, 'watchers': val}}
        data = json.dumps(p_dict, indent=4)

        if os.stat(self.wl_file_name).st_size == 0:
            data = '{\n' + data[1:len(data) - 1]
        else:
            data = ',' + data[1:len(data) - 1]

        with open(self.wl_file_name, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.writelines(data)
            fcntl.flock(f, fcntl.LOCK_UN)
        pass

    def remove_file_from_suite(self, fname):
        with open(self.test_suite, 'r') as f:
            lines = f.readlines()
        with open(self.test_suite, 'w') as f:
            new_lines = [line for line in lines if line.strip('\n') != fname]
            f.writelines(new_lines)

        pass

    def add_existing_test_case_to_suite(self, tc_name):
        # self.wl_fd.close()

        if os.stat(self.wl_file_name).st_size == 0:
            self.remove_file_from_suite(self.wl_file_name)
            self.append_file_to_suite(utils.get_file_name(tc_name))
            self.append_file_to_suite(self.wl_file_name)
        else:
            self.contd_count = self.contd_count + 1

            try:
                is_contd_present = self.wl_file_name.find('_contd_')
                if is_contd_present == -1:
                    self.wl_file_name = self.wl_file_name[:-5] + '_contd_1.json'
                else:
                    offset = is_contd_present + len('_contd_')
                    self.wl_file_name = self.wl_file_name[0:offset] + '{}.json'.format(self.contd_count)
                # self.wl_fd = open(self.wl_file_name, "w")
            except Exception as e:
                utils.m_log_err('failed to open new watch_list file')
                utils.m_log_err('Exception : {}'.format(e))
                sys.exit(1)

            self.append_file_to_suite(utils.get_file_name(tc_name))
            self.append_file_to_suite(self.wl_file_name)

    def append_file_to_suite(self, fname):
        self.g_cmd_no = 0
        # append the newly created watch list file to test_suite
        while True:
            try:
                with open(self.test_suite, 'a+') as wl_suite:
                    fcntl.flock(wl_suite, fcntl.LOCK_EX)
                    wl_suite.writelines('\n'+fname)
                    fcntl.flock(wl_suite, fcntl.LOCK_UN)
                    wl_suite.flush()
                    break
            except IOError:
                continue

        with open(g_curr_tc_name_holder, 'w') as f:
            f.writelines(fname)

    def exec_and_process_output(self, cmd, exec_oly=False) -> []:
        try:
            stdout = utils.run_command(self.chan, cmd)
        except Exception as e:
            utils.m_log_excp('Command execution Failed')
            utils.m_log_excp('Received exception : {}'.format(e))
            return []

        if exec_oly:
            print(stdout.partition('\n')[2])
            return []

        watchers = []
        if cmd.startswith(utils.show_cmd_pattern):
            ret = utils.process_show_output(cmd, stdout)
            if ret == (-1, -1):
                return []
            else:
                re_table, fsm_results = ret

            if not 'y' == input('Add watchers ? [y/n]'):
                return []

            key_col_id = utils.read_int_in_range('key column index (-1 no key): ', -1, len(re_table.header))

            if key_col_id != -1:
                i = 0
                invalid_key = False
                for row in fsm_results:
                    if row[key_col_id] == '':
                        print('%Error : key cant be empty @ row-{}'.format(i))
                        invalid_key = True
                        break
                    i = i + 1
                if invalid_key:
                    return []
                key_col_name = re_table.header[key_col_id]
            else:
                key_col_name = 'NA'

            col_str = ''
            row_str = ''
            while True:
                if col_str == '-1' and row_str == '-1':
                    break

                if key_col_id == -1:
                    col_str = '-1'
                    row_str = input('watch>> (row_list) : ')
                    if row_str == 'end':
                        break
                    elif re.match(r'[,\d]', row_str) or row_str != '-1':
                        print('%Error% Invalid Input')
                        print('FORMAT ->> row-index-list')
                        print('\'end\' to stop')
                        print('ex:')
                        print('1,2,3 >> watch rows 1,2,3')
                        print('-1    >> watch all rows')
                        continue
                else:
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
                    row_list = re.findall(r'[\d]+', row_str)
                    row_list = list(map(int, row_list))
                    invalid_row_id = False
                    row_id = 0
                    for row_id in row_list:
                        if row_id >= len(fsm_results):
                            invalid_row_id = True
                            break

                    if invalid_row_id:
                        print('%Error row id {} > max rows {}'.format(row_id, len(fsm_results)))
                        continue

                if col_str == '-1':
                    col_list = list(range(0, len(re_table.header)))
                else:
                    col_list = re.findall(r'[\d]+', col_str)
                    col_list = list(map(int, col_list))
                    invalid_col_id = False
                    col_id = 0
                    for col_id in col_list:
                        if col_id >= len(re_table.header):
                            invalid_col_id = True
                            break

                    if invalid_col_id:
                        print('%Error col id {} > max cols {}'.format(col_id, len(re_table.header)))
                        continue

                watchers.append({'watch-key': key_col_name})
                for row in row_list:
                    if row >= len(fsm_results):
                        continue
                    row_dict = dict(zip(re_table.header, fsm_results[row]))
                    # add key as 1st elem in dict
                    if key_col_name != 'NA':
                        user_dict = {key_col_name: row_dict[key_col_name]}
                    else:
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
            utils.m_log_info('Watchlist : \n{}'.format(watchers))
        else:
            print(stdout.partition('\n')[2])

        return watchers

    def exec_and_process_output_adv_mode(self, cmd, exec_oly=False) -> []:
        try:
            stdout = utils.run_command(self.chan, cmd)
        except Exception as e:
            utils.m_log_excp('Command execution Failed')
            utils.m_log_excp('Received exception : {}'.format(e))
            return []

        if exec_oly:
            print(stdout.partition('\n')[2])
            return []

        watchers = []
        if cmd.startswith(utils.show_cmd_pattern):
            ret = utils.process_show_output(cmd, stdout)
            if ret == (-1, -1):
                return []
            else:
                re_table, fsm_results = ret

            if not 'y' == input('Add watchers ? [y/n]'):
                return []

            new_vars = {}
            if 'y' == input('Add variables ? [y/n]'):
                fsm_results, new_vars = utils.add_runtime_variables(re_table.header, fsm_results
                                                                    , len(fsm_results), len(re_table.header))

            key_col_id = utils.read_int_in_range('key column index (-1 no key): ', -1, len(re_table.header))

            if key_col_id != -1:
                i = 0
                invalid_key = False
                for row in fsm_results:
                    if row[key_col_id] == '':
                        print('%Error : key cant be empty @ row-{}'.format(i))
                        invalid_key = True
                        break
                    i = i + 1
                if invalid_key:
                    return []
                key_col_name = re_table.header[key_col_id]
            else:
                key_col_name = 'NA'

            col_str = ''
            row_str = ''
            while True:
                if col_str == '-1' and row_str == '-1':
                    break

                if key_col_id == -1:
                    col_str = '-1'
                    row_str = input('watch>> (row_list) : ')
                    if row_str == 'end':
                        break
                    elif not (re.match(r'[,\d]', row_str) or row_str != '-1'):
                        print('%Error% Invalid Input')
                        print('FORMAT ->> row-index-list')
                        print('\'end\' to stop')
                        print('ex:')
                        print('1,2,3 >> watch rows 1,2,3')
                        print('-1    >> watch all rows')
                        continue
                else:
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
                    row_list = re.findall(r'[\d]+', row_str)
                    row_list = list(map(int, row_list))
                    invalid_row_id = False
                    row_id = 0
                    for row_id in row_list:
                        if row_id >= len(fsm_results):
                            invalid_row_id = True
                            break

                    if invalid_row_id:
                        print('%Error row id {} > max rows {}'.format(row_id, len(fsm_results)))
                        continue

                if col_str == '-1':
                    col_list = list(range(0, len(re_table.header)))
                else:
                    col_list = re.findall(r'[\d]+', col_str)
                    col_list = list(map(int, col_list))
                    invalid_col_id = False
                    col_id = 0
                    for col_id in col_list:
                        if col_id >= len(re_table.header):
                            invalid_col_id = True
                            break

                    if invalid_col_id:
                        print('%Error col id {} > max cols {}'.format(col_id, len(re_table.header)))
                        continue

                watchers.append({'watch-key': key_col_name})
                for row in row_list:
                    if row >= len(fsm_results):
                        continue
                    row_dict = dict(zip(re_table.header, fsm_results[row]))
                    # add key as 1st elem in dict
                    if key_col_name != 'NA':
                        user_dict = {key_col_name: row_dict[key_col_name]}
                    else:
                        user_dict = {}
                    for col in col_list:
                        if col >= len(re_table.header):
                            continue
                        col_name = re_table.header[col]
                        if str(row)+'_'+col_name in new_vars.keys():
                            user_dict[col_name] = new_vars[str(row)+'_'+col_name]
                        else:
                            user_dict[col_name] = row_dict[col_name]
                    # end for col in col_list:
                    watchers.append(user_dict)
                # end for row in row_list
            # end while True for watchlist
            utils.m_log_info('Watchlist : \n{}'.format(watchers))
        else:
            print(stdout.partition('\n')[2])

        return watchers

    def launch_monitor_terminal_adv_mode(self):
        while True:
            cmd = input('Advanced mode# ')
            cmd = cmd.strip()

            if cmd in ['q', 'exit', 'quit']:
                break
            elif cmd in ['su', 'sudo su']:
                print('cant enter super user mode from this terminal')
                continue
            elif cmd in ['', 'h', 'help', '?']:
                print('exit/quit/q  - stop this session.')
                continue
            elif cmd.startswith('ex>'):
                self.exec_and_process_output(cmd[3:], exec_oly=True)
                continue
            if not cmd.startswith('sudo'):
                cmd = 'sudo ' + cmd

            watchers = []
            if cmd.startswith('sudo sleep'):
                r1 = re.search(r'sudo sleep (?!$)([\d]*[.]?(?!$)[\d]*)', cmd)
                if len(r1.groups()) != 1:
                    print('Provide a valid float value to sleep, refer time.sleep')
                    continue
            else:
                watchers = self.exec_and_process_output_adv_mode(cmd)

            self.add_cmd_to_curr_wl(cmd, val=watchers)


    def launch_monitor_terminal(self) -> None:
        """
        Launch a terminal and capture all actions happening on this terminal.
        we will create a watch_list file to generate automation script.
        :return: None
        """
        cmd = 'whoami && date'
        try:
            stdout = utils.run_command(self.chan, cmd)
        except Exception as e:
            utils.m_log_excp('Command execution Failed')
            utils.m_log_excp('Received exception : {}'.format(e))
            return
        utils.m_log_info(stdout)

        while True:
            cmd = input('sonic# ')
            cmd = cmd.strip()

            if cmd in ['q', 'exit', 'quit']:
                break
            elif cmd in ['su', 'sudo su']:
                print('cant enter super user mode from this terminal')
                continue
            elif cmd in ['', 'h', 'help', '?']:
                print('exit/quit/q  - stop this session.')
                print('mr_new    <tc_name:str> - create a new watch_list file')
                print('mr_insert <tc_name:str> - insert a existing watch_list to be run from this point')
                continue
            elif cmd == 'mr_adv':
                self.launch_monitor_terminal_adv_mode()
            elif cmd.startswith('mr_insert '):
                tc_name = cmd.split(' ')[1]
                if not os.path.exists(utils.get_file_name(tc_name)):
                    print('Test case file doesnt exists')
                    continue
                self.add_existing_test_case_to_suite(tc_name)
                continue
            elif cmd.startswith('mr_new '):
                option = ''
                if len(cmd.split(' ')) == 3:
                    option = cmd.split(' ')[2]

                tc_name = cmd.split(' ')[1]
                if tc_name.find('.') != -1:
                    print('file name should not have "."')
                    print('do not type file extension')
                else:
                    if option != '-y':
                        if os.path.exists(utils.get_file_name(tc_name)):
                            if 'n' == input('Test case file already exists, overwrite? [y/n]').strip():
                                continue

                    if os.stat(self.wl_file_name).st_size == 0:
                        self.remove_file_from_suite(self.wl_file_name)
                    self.wl_file_name = utils.get_file_name(tc_name)
                    self.create_new_watch_list_file(append_to_suite=True)
                continue
            elif cmd.startswith('ex>'):
                self.exec_and_process_output(cmd[3:], exec_oly=True)
                continue

            if not cmd.startswith('sudo'):
                cmd = 'sudo ' + cmd

            watchers = []
            if cmd.startswith('sudo sleep'):
                r1 = re.search(r'sudo sleep (?!$)([\d]*[.]?(?!$)[\d]*)', cmd)
                if len(r1.groups()) != 1:
                    print('Provide a valid float value to sleep, refer time.sleep')
                    continue
            else:
                watchers = self.exec_and_process_output(cmd)

            self.add_cmd_to_curr_wl(cmd, val=watchers)
        # End of while True
    pass
