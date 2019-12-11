from setuptools import setup

setup(
    name='mr',
    version='0.1',
    py_modules=['mr'],
    install_requires=[
        'Click', 'paramiko', 'tabulate', 'textfsm'
    ],
    entry_points='''
        [console_scripts]
        yourscript=mr:monitor_replay
    ''',
)
