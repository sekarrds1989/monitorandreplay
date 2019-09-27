import os
import argparse
parser = argparse.ArgumentParser(description='Monitor-Replay launcher.')

parser.add_argument('mode', choices=['monitor', 'replay'])
args = parser.parse_args()
print(args)


dut_connections = {'D1': {'ip': '10.59.136.31', 'port': '22'},
                   'D2': {'ip': '10.59.136.32', 'port': '22'}
                   }

if args.mode == 'monitor':
    # erase contents of the file
    open('watch_list.json', 'w').close()

    for dut in dut_connections.keys():
            os.system(
                'xterm -fa \'Monospace\' -fs 12 -bg black -fg white -geometry 100x50 -sb -title %s \
                -e "date; echo connect to %s; python3.7 ./mr.py monitor %s; $SHELL"&'
                % (dut, dut_connections[dut]['ip'], dut_connections[dut]['ip']))
else:
    with open('watch_list.json', 'a') as f:
        f.writelines('}')
        f.close()
    os.system(
        'xterm -fa \'Monospace\' -fs 12 -bg black -fg white -geometry 100x50 -sb -title Replay \
        -e "date; python3.7 ./mr.py replay; $SHELL"&')

