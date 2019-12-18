import topo
import os
import utils
import json


def generate_idp_file(idp_name):
    wl_tc_dict_list = []
    while True:
        tc_name = input('Tc Name : ')
        if tc_name == 'end':
            break

        if not os.path.exists(tc_name):
            print('file doesnt exists')
            continue

        wl_dict = utils.read_json_file_as_dict(tc_name)
        if wl_dict is None:
            continue

        wl_tc_dict_list.append({tc_name: wl_dict})

    try:
        os.makedirs(os.path.dirname(idp_name))
    except Exception:
        print('{} Exists'.format(os.path.dirname(idp_name)))

    with open(idp_name, 'w') as idp:

        idp.write('\n\n"""***************TOPO**************"""\n\n')
        with open('topo.py', 'r') as ut:
            lines = ut.readlines()
        idp.writelines(lines)
        idp.write('dcon = dut_connections')

        idp.write('\n\n"""***************RUN TIME VARS**************"""\n\n')
        p_dict = utils.read_json_file_as_dict(topo.g_rt_vars_file)
        idp.write('rt_vars_dict = ')
        json.dump(p_dict, idp, indent=4)

        idp.write('\n\n"""****************SETUP Needed packages**************"""\n\n')
        idp.write('mr_req_pkgs = ["jsonlib==1.2.7",\n')
        idp.write('               "textfsm==1.1.0",\n')
        idp.write('               "tabulate==0.8.4"]\n')

        idp.write('with open("/tmp/requirements.txt", "w") as f:\n')
        idp.write('    f.writelines(mr_req_pkgs)\n')

        idp.write('mr_setup_bash = ["if [ -d ~/mr_env ]; \
        then echo \\"Venv is already setup\\" && exit 1; fi\\n",\n')
        idp.write('                 "pushd ~\\n",\n')
        idp.write('                 "python3 -m venv mr_env\\n",\n')
        idp.write('                 "source mr_env/bin/activate\\n",\n')
        idp.write('                 "pip install --upgrade pip\\n",\n')
        idp.write('                 "pip install -r /tmp/requirements.txt\\n",\n')
        idp.write('                 "deactivate\\n",\n')
        idp.write('                 "popd\\n"]\n')

        idp.write('with open("/tmp/mr_setup.sh", "w") as f:\n')
        idp.write('    f.writelines(mr_setup_bash)\n')

        idp.write('import sys\n')
        idp.write('import os\n')
        idp.write('import stat\n')

        idp.write('st = os.stat("/tmp/mr_setup.sh")\n')
        idp.write('os.chmod("/tmp/mr_setup.sh", st.st_mode | stat.S_IEXEC)\n')
        idp.write('os.system("/tmp/mr_setup.sh")\n')

        idp.write('from os.path import expanduser\n')
        idp.write('sys.path.append("{}/mr_env/lib/python3.7/site-packages/".format(expanduser("~")))\n')

        idp.write('\n\n"""***************COMMAND to TEMPLATE Mapping**************"""\n\n')
        cmd_to_tmpl_map_dict = utils.read_json_file_as_dict(topo.cmd_to_template_map)
        idp.write('cmd_to_tmpl_map_dict = ')
        json.dump(cmd_to_tmpl_map_dict, idp, indent=4)

        idp.write('\n\n"""***************Template Files**************"""\n\n')
        tmpl_data_dict = {}
        for key, tmpl_name in cmd_to_tmpl_map_dict.items():
            with open(topo.templates_dir + tmpl_name, 'r') as f:
                tmpl_data_dict[key] = f.readlines()
        idp.write('tmpl_data_dict = ')
        json.dump(tmpl_data_dict, idp, indent=4)

        idp.write('\n\n"""***************WATCH-LISTS**************"""\n\n')
        idp.write('g_wl_tc_dict_list = ')
        json.dump(wl_tc_dict_list, idp, indent=4)

        idp.write('\n\n"""***************UTILS**************"""\n\n')
        with open('utils.py', 'r') as ut:
            lines = ut.readlines()
            for line in lines:
                line = line.replace('utils.', '')
                line = line.replace('topo.', '')
                if line.strip().startswith(('from topo import', 'import utils as utils', 'import topo')):
                    continue
                idp.write(line)

        idp.write('\n\n"""***************REPLAY&TEST**************"""\n\n')
        with open('replay_and_test.py', 'r') as rt:
            lines = rt.readlines()
            for line in lines:
                line = line.replace('utils.', '')
                line = line.replace('topo.', '')
                if line.strip().startswith(('import topo', 'from topo import', 'import utils as utils')):
                    continue
                idp.write(line)

        idp.write('\n\n"""***************MAIN**************"""\n\n')
        idp.write('if __name__== "__main__":\n')
        idp.write('    import os\n')
        idp.write('    try:\n')
        idp.write('        os.mkdir("{}")\n'.format(topo.logs_dir))
        idp.write('    except Exception:\n')
        idp.write('        print("Logs Folder exists")\n\n')
        idp.write('    try:\n')
        idp.write('        os.makedirs("{}")\n'.format(os.path.dirname(topo.g_rt_vars_file)))
        idp.write('    except Exception:\n')
        idp.write('        print("{} Folder exists")\n\n'.format(os.path.dirname(topo.g_rt_vars_file)))

        idp.write('    replay_logger_init()\n')
        idp.write('    for dut in dcon.keys():\n')
        idp.write('        dc = DutClients(dut, dcon[dut]["ip"], "22", "admin", "broadcom")\n')
        idp.write('        g_dut_clients[dcon[dut]["ip"]] = dc\n\n')

        idp.write('    backup_rt_vars_file(g_rt_vars_file)\n')
        idp.write('    with open(g_rt_vars_file, "w") as rt:\n')
        idp.write('        json.dump(rt_vars_dict, rt, indent=4)\n\n')

        idp.write('    with open("{}", "w") as f:\n'.format(topo.cmd_to_template_map))
        idp.write('        json.dump(cmd_to_tmpl_map_dict, f, indent=4)\n\n')

        idp.write('    try:\n')
        idp.write('        os.makedirs("{}")\n'.format(topo.templates_dir))
        idp.write('    except Exception:\n')
        idp.write('        print("templates Folder exists")\n')

        idp.write('    for key in tmpl_data_dict.keys():\n')
        idp.write('        with open("{}"+cmd_to_tmpl_map_dict[key], "w") as f:\n'.format(topo.templates_dir))
        idp.write('            f.writelines(tmpl_data_dict[key])\n\n')

        idp.write('    for tc_wl_dict in g_wl_tc_dict_list:\n')
        idp.write('        tc_name, wl_dict = tc_wl_dict.popitem()\n')
        idp.write('        process_commands(tc_name, wl_dict)\n')

    # idp_file write completed

