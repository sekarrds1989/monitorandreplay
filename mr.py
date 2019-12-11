import monitor as mt
import replay_and_test as rt
import click
import utils as utils


@click.group('mr')
@click.option('-g', '--gdb', is_flag=True, help='stop at pdb on error')
@click.option('--test_suite', help='test suite name')
@click.option('--tc_name', help='test suite name')
@click.pass_context
def monitor_replay(ctx, gdb, test_suite, tc_name=''):
    """ monitor and replay commands on ssh terminal"""
    ctx.obj['tc_name'] = ''
    ctx.obj['test_suite'] = ''

    if gdb:
        utils.g_pdb_set = True

    if tc_name:
        ctx.obj['tc_name'] = tc_name
    elif test_suite:
        ctx.obj['test_suite'] = test_suite
    else:
        utils.m_log_err('No test suite or tc_name given ')
        exit(-1)
    pass


@monitor_replay.command('monitor')
@click.argument('ip', required=True)
@click.pass_context
def mr_monitor(ctx, ip):
    """ monitor the session and store commands in watchlist.json"""
    utils.monitor_logger_init()

    utils.m_log_debug('Create Test Suite {}'.format(ctx.obj['test_suite']))
    dut: mt.DutListener = mt.DutListener(ip, ctx.obj['test_suite'], 'admin', 'broadcom')
    dut.launch_monitor_terminal()
    pass


@monitor_replay.command('replay')
@click.pass_context
def mr_replay(ctx):
    """ Read watchlist.json and replay configs in device"""
    utils.replay_logger_init()

    if ctx.obj['tc_name']:
        utils.m_log_debug('Start Test case : {}'.format(ctx.obj['tc_name']))
    else:
        utils.m_log_debug('Start Test suite : {}'.format(ctx.obj['test_suite']))

    rt.start_automation(ctx.obj['test_suite'], ctx.obj['tc_name'])
    pass


if __name__ == '__main__':
    monitor_replay(obj={})

    pass
