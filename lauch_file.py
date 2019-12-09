import os
from topo import dut_connections as dcon
import click

"""
This is a launcher file.
For monitor, it will open a terminal for each dut listed in topo.py
For replay , it will open 1 terminal

And execute the appropriate command on the terminal.
"""


@click.group('launchmr')
@click.pass_context
@click.option('-g', '--gdb', is_flag=True, help='stop at pdb on error')
def launch_mr(ctx, gdb):
    ctx.obj['options'] = ''
    if gdb:
        ctx.obj['options'] += ' --gdb'
    pass


@launch_mr.command('monitor')
@click.pass_context
def launch_mr_monitor(ctx):
    # erase contents of the file
    open('watch_list.json', 'w').close()
    open('logs/mrlog.log', 'w').close()

    for dut in dcon.keys():
        with open('{}_monitor.sh'.format(dut), 'w') as d1bash:
            d1bash.writelines('#!/bin/bash\
            \n\ncd /Users/dr412113/PycharmProjects/monitorandreplay\
            \necho connect to {}\npython3.7 ./mr.py {} monitor {} {}\
            \nbash'.format(dut, ctx.obj['options'], dcon[dut]['ip'], dcon[dut]['port']))

        os.system('chmod +x %s_monitor.sh'%(dut))
        os.system('open -a Terminal %s_monitor.sh'%(dut))


@launch_mr.command('replay')
@click.pass_context
def launch_mr_replay(ctx):
    with open('replay.sh', 'w') as d1bash:
        d1bash.writelines('#!/bin/bash\
        \n\ncd /Users/dr412113/PycharmProjects/monitorandreplay\
        \npython3.7 ./mr.py {} replay\
        \nbash'.format(ctx.obj['options']))
    os.system('chmod +x replay.sh')
    os.system('open -a Terminal replay.sh')


if __name__ == '__main__':
    launch_mr(obj={})
    pass

