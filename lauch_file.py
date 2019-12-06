import os
import argparse
from topo import dut_connections as dcon

parser = argparse.ArgumentParser(description='Monitor-Replay launcher.')

parser.add_argument('mode', choices=['monitor', 'replay'])
args = parser.parse_args()
print(args)


if args.mode == 'monitor':
    # erase contents of the file
    open('watch_list.json', 'w').close()

    for dut in dcon.keys():
            os.system(
                'xterm -fa \'Monospace\' -fs 12 -bg black -fg white -geometry 100x50 -sb -title %s \
                -e "date; echo connect to %s; python3.7 ./mr.py monitor %s; $SHELL"&'
                % (dut, dcon[dut]['ip'], dcon[dut]['ip']))
else:
    os.system(
        'xterm -fa \'Monospace\' -fs 12 -bg black -fg white -geometry 100x50 -sb -title Replay \
        -e "date; python3.7 ./mr.py replay; $SHELL"&')

