import os
from topo import dut_connections as dcon
from topo import g_curr_tc_name_holder
import topo

import click
import utils as utils

"""
This is a launcher file.
For monitor, it will open a terminal for each dut listed in topo.py
For replay , it will open 1 terminal

And execute the appropriate command on the terminal.
"""


@click.group('launchmr')
@click.pass_context
@click.option('-g', '--gdb', is_flag=True, help='stop at pdb on error')
@click.option('--test_suite', help='test suite name')
@click.option('--tc_name', help='test suite name')
def launch_mr(ctx, gdb, test_suite='', tc_name=''):
    ctx.obj['options'] = ''
    ctx.obj['tc_name'] = ''
    ctx.obj['test_suite'] = ''

    if gdb:
        ctx.obj['options'] += ' --gdb'

    # ctx.obj['test_suite'] = 'watch_lists/' + input('Test Suite Name : watch_lists/')
    if tc_name:
        ctx.obj['tc_name'] = tc_name
    elif test_suite:
        ctx.obj['test_suite'] = test_suite
    else:
        print('No test suite or tc_name given ')
        exit(-1)
    pass


@launch_mr.command('monitor')
@click.pass_context
def launch_mr_monitor(ctx):
    # erase contents of the file

    if not ctx.obj['test_suite']:
        print('Monitor cant start. Test-suite name is not given')
        exit(-1)

    options = ctx.obj['options']
    options += ' --test_suite ' + ctx.obj['test_suite']

    if os.path.exists(ctx.obj['test_suite']):
        if os.path.isdir(ctx.obj['test_suite']):
            print('{} is a directory'.format(ctx.obj['test_suite']))
            exit(1)
        if 'n' == input('Test Suite already exists, overwrite? [y/n]').strip():
            exit(1)

    os.makedirs(os.path.dirname(ctx.obj['test_suite']), exist_ok=True)
    with open(ctx.obj['test_suite'], 'w') as f:
        suite_name = '{}_init.json'.format(ctx.obj['test_suite'])
        f.writelines('\n')  # start with \n for simplifiying last line read
        f.writelines(suite_name)
    with open(g_curr_tc_name_holder, 'w') as f:
        f.writelines(suite_name)

    open('{}_init.json'.format(ctx.obj['test_suite']), 'w').close()
    open(topo.logs_dir+'mrlog.log', 'w').close()
    utils.create_rt_vars_file()

    if 'gdb' in options:
        invoke_inbuilt_pdb = '-m pdb -c continue '
    else:
        invoke_inbuilt_pdb = ''

    for dut in dcon.keys():
        with open('{}_monitor.sh'.format(topo.mr_ctl_dir+dut), 'w') as d1bash:
            d1bash.writelines('#!/bin/bash\
            \n\ncd /Users/dr412113/PycharmProjects/monitorandreplay\
            \necho connect to {}\npython3.7 {} ./mr.py {} monitor {}\
            \nbash\n'.format(dut, invoke_inbuilt_pdb, options, dcon[dut]['ip']))

        os.system('chmod +x {}_monitor.sh'.format(topo.mr_ctl_dir+dut))
        os.system('open -a Terminal {}_monitor.sh'.format(topo.mr_ctl_dir+dut))


@launch_mr.command('replay')
@click.pass_context
def launch_mr_replay(ctx):
    options = ctx.obj['options']

    if ctx.obj['tc_name']:
        options += ' --tc_name ' + ctx.obj['tc_name']
    else:
        options += ' --test_suite ' + ctx.obj['test_suite']

    if 'gdb' in options:
        invoke_inbuilt_pdb = '-m pdb -c continue '
    else:
        invoke_inbuilt_pdb = ''

    with open('{}replay.sh'.format(topo.mr_ctl_dir), 'w') as d1bash:
        d1bash.writelines('#!/bin/bash\
        \n\ncd /Users/dr412113/PycharmProjects/monitorandreplay\
        \npython3.7 {} ./mr.py {} replay\
        \nbash'.format(invoke_inbuilt_pdb, options))
    os.system('chmod +x {}replay.sh'.format(topo.mr_ctl_dir))
    os.system('open -a Terminal {}replay.sh'.format(topo.mr_ctl_dir))


if __name__ == '__main__':
    launch_mr(obj={})
    pass
