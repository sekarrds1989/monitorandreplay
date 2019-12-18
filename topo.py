dut_connections = {
    'D1': {'ip': '10.59.132.169'},
    'D2': {'ip': '10.59.132.170'}
}

dut_ports = {
    'D1': {'P1': 'Ethernet64', 'P1_1': 'Ethernet 64'},
    'D2': {'P1': 'Ethernet64', 'P1_1': 'Ethernet 64'}
}

logs_dir                = './logs/'
mr_ctl_dir              = './mr_ctl/'
g_is_exisiting_tc_reopened = mr_ctl_dir+'mr_is_reopened_for_append'
g_curr_tc_name_holder   = mr_ctl_dir+'mr_curr_test'
g_rt_vars_file          = mr_ctl_dir+'rt_vars/rt_vars.txt'
wl_dir                  = mr_ctl_dir+'watch_lists/'
templates_dir           = mr_ctl_dir+'templates/'
cmd_to_template_map     = mr_ctl_dir+'cmd_template_map.json'
