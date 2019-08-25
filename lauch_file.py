import os
dut_connections = {'D1': {'ip': '10.59.136.26', 'port': '22'},
                   'D2': {'ip': '10.59.136.27', 'port': '22'}
                   }

for dut in dut_connections.keys():
    os.system(
        'xterm -geometry 300x150 -sb -title %s \
        -e "date; echo connect to %s; python3.7 ./mr.py monitor %s; $SHELL"&'
        % (dut, dut_connections[dut]['ip'], dut_connections[dut]['ip']))
