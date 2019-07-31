import sys
import monitor as monitor
import click
import utils as utils


@click.group('mr')
def monitor_replay():
    """ monitor and replay commands on ssh terminal"""
    pass


@monitor_replay.command('monitor')
@click.argument('ip',required=True)
@click.argument('port')
def mr_monitor(ip, port='22'):
    """ monitor the session and store commands in watchlist.json"""

    utils.log_dbg('start a monitor session')
    dut: monitor.DutListener = monitor.DutListener(ip, port, 'admin', 'broadcom')
    dut.launch_terminal()
    pass


@monitor_replay.command('replay')
@click.argument('ip',required=True)
@click.argument('port')
def mr_replay(ip, port='22'):
    """ Read watchlist.json and replay configs in device"""

    utils.log_dbg('start a replay_test session')
    pass


@monitor_replay.command('exec_mode')
@click.argument('ip', required=True)
@click.argument('port')
def mr_exec(ip, port='22'):
    """ Create a exec only mode"""

    utils.log_dbg('start a exec only session')
    dut: monitor.DutListener = monitor.DutListener(ip, port, 'admin', 'broadcom', exec_mode=True)
    dut.launch_terminal()
    pass


if __name__ == '__main__':
    try:
        fptr = open('watch_list.json', "a+")
    except Exception as e:
        utils.log_dbg('failed to open watch_list file')
        utils.log_err('Exception : {}'.format(e))
        sys.exit(1)

    monitor_replay()

    pass
