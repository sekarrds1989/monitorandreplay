import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
from dut_listener import process_show_output
import json
import glob
import re

g_wl_data = {}
g_dut_list = []
g_client_list = []
g_uname = 'admin'
g_pwd = 'password'


def build_automation_infra():
    global g_dut_list
    global g_wl_data

    with open('watch_list.json', 'r') as wl:
        g_wl_data = json.load(wl)

    for key in g_wl_data.keys():
        if key not in g_dut_list:
            g_dut_list.append(key)

    for dut in g_dut_list:
        client = pc.SSHClient()
        g_client_list[dut] = client

        try:
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(dut, username=g_uname, password=g_pwd)
        except Exception as e:
            print('Client connection Failed : {} {} {} {}'.format(dut, '22', g_uname, g_pwd))
            print('Received exception : {}'.format(e))
            client.close()
            sys.exit(1)

    pass


def start_automation():
    for key,val in g_wl_data.items():
        client = g_client_list[key]
        cmd = val['cmd']
        watch_list = val['watch_list']
        stdin, stdout, stderr = client.exec_command(val['cmd'])
        lines = stderr.readlines()
        if len(lines):
            for line in lines:
                print('{}'.format(line.strip()))
            continue
        if cmd.startswith('sudo show'):
            ret = process_show_output(cmd, stdout)
            if ret is None:
                print('FAILED : \n{}: {}'.format(key,val))
                return
            else:
                re_table, fsm_results = ret

            match_count = 0
            # compare show output with watch_list
            for subset in watch_list.items():
                match_found = False
                for row in fsm_results:
                    superset = dict(zip(re_table.header, row))
                    # check if subset in superset
                    if subset.viewitems() <= superset.viewitems():
                        match_found = True
                        match_count += 1
                        break
                if not match_found:
                    print('match not found for {}'.format(subset))
                    print('FAILED : \n{}: {}'.format(key,val))
                    return

            print('PASS')
    pass


if __name__ == '__main__':
    build_automation_infra()
    start_automation()
