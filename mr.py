import monitor as mt
import replay_and_test as rt
import click
import utils as utils


@click.group('mr')
@click.option('-g', '--gdb', is_flag=True, help='stop at pdb on error')
def monitor_replay(gdb):
    """ monitor and replay commands on ssh terminal"""
    if gdb:
        utils.g_pdb_set = True
    pass


@monitor_replay.command('monitor')
@click.argument('ip',required=True)
@click.argument('port',required=True)
def mr_monitor(ip, port='22'):
    """ monitor the session and store commands in watchlist.json"""

    utils.log_debug('start a monitor session')
    dut: mt.DutListener = mt.DutListener(ip, port, 'admin', 'broadcom')
    dut.launch_terminal()
    pass


@monitor_replay.command('replay')
def mr_replay():
    """ Read watchlist.json and replay configs in device"""

    utils.log_debug('start a replay_test session')
    rt.setup_automation_infra()
    rt.start_automation()
    pass


@monitor_replay.command('exec_mode')
@click.argument('ip', required=True)
@click.argument('port',required=True)
def mr_exec(ip, port='22'):
    """ Create a exec only mode"""

    utils.log_debug('start a exec only session')
    dut: mt.DutListener = mt.DutListener(ip, port, 'admin', 'broadcom', exec_only_mode=True)
    dut.launch_terminal()
    pass


if __name__ == '__main__':
    utils.logger_init()
    monitor_replay()
    pass
