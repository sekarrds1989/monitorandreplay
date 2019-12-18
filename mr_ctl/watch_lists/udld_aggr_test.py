

"""***************TOPO**************"""

dut_connections = {
    'D1': {'ip': '10.59.136.31'},
    'D2': {'ip': '10.59.136.32'}
}

dut_ports = {
    'D1': {'P1': 'Ethernet26', 'P1_1': 'Ethernet 26'},
    'D2': {'P1': 'Ethernet26', 'P1_1': 'Ethernet 26'}
}
g_curr_tc_name_holder = './mr_curr_test'

dcon = dut_connections

"""***************WATCH-LISTS**************"""

g_wl_tc_dict_list = [
    {
        "watch_lists/udld_deinit.json": {
            "D1-0": {
                "cmd": "sudo udldctl rx_drop disable D1P1",
                "watchers": []
            },
            "D2-0": {
                "cmd": "sudo udldctl rx_drop disable D2P1",
                "watchers": []
            },
            "D1-1": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"no udld aggressive\"",
                "watchers": []
            },
            "D1-2": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"no udld multiplier\"",
                "watchers": []
            },
            "D1-3": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"no udld message-time\"",
                "watchers": []
            },
            "D1-4": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"no udld enable\"",
                "watchers": []
            },
            "D2-1": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"no udld aggressive\"",
                "watchers": []
            },
            "D1-5": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface D1P1_1\" -c \"no udld enable\"",
                "watchers": []
            },
            "D2-2": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"no udld multiplier\"",
                "watchers": []
            },
            "D1-6": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface D1P1_1\" -c \"shutdown\"",
                "watchers": []
            },
            "D2-3": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"no udld message-time\"",
                "watchers": []
            },
            "D2-4": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"no udld enable\"",
                "watchers": []
            },
            "D2-5": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface D2P1_1\" -c \"no udld enable\"",
                "watchers": []
            },
            "D2-6": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface D2P1_1\" -c \"shutdown\"",
                "watchers": []
            },
            "D2-7": {
                "cmd": "sudo udldctl global",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "IS_ENABLED": "N",
                        "IS_AGGR": "N",
                        "MSG_INTV": "0",
                        "MULTIPLIER": "0",
                        "TIMEOUT_INTV": "0"
                    }
                ]
            },
            "D1-7": {
                "cmd": "sudo udldctl global",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "IS_ENABLED": "N",
                        "IS_AGGR": "N",
                        "MSG_INTV": "0",
                        "MULTIPLIER": "0",
                        "TIMEOUT_INTV": "0"
                    }
                ]
            },
            "D1-8": {
                "cmd": "sudo udldctl port D1P1",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "D1P1",
                        "CFG_ENABLE": "N",
                        "CFG_AGGR": "N",
                        "OPER_AGGR": "N",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "NA",
                        "OPER_UDLDSTATE": "NA",
                        "OPER_PHASE": "START",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D2-8": {
                "cmd": "sudo udldctl port D2P1",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "D2P1",
                        "CFG_ENABLE": "N",
                        "CFG_AGGR": "N",
                        "OPER_AGGR": "N",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "NA",
                        "OPER_UDLDSTATE": "NA",
                        "OPER_PHASE": "START",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            }
        }
    },
    {
        "watch_lists/udld_init_aggr.json": {
            "D1-1": {
                "cmd": "sudo udldctl global",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "IS_ENABLED": "N",
                        "IS_AGGR": "N",
                        "MSG_INTV": "0",
                        "MULTIPLIER": "0",
                        "TIMEOUT_INTV": "0"
                    }
                ]
            },
            "D1-2": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"udld enable\"",
                "watchers": []
            },
            "D1-3": {
                "cmd": "sudo udldctl global",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "IS_ENABLED": "Y",
                        "IS_AGGR": "N",
                        "MSG_INTV": "1",
                        "MULTIPLIER": "3",
                        "TIMEOUT_INTV": "3"
                    }
                ]
            },
            "D1-4": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "N",
                        "CFG_AGGR": "N",
                        "OPER_AGGR": "N",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "NA",
                        "OPER_UDLDSTATE": "NA",
                        "OPER_PHASE": "START",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D1-5": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface Ethernet 26\" -c \"udld enable\"",
                "watchers": []
            },
            "D1-6": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "N",
                        "OPER_AGGR": "N",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "INDETERM",
                        "OPER_PHASE": "LINKUP",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D1-7": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"udld aggressive\"",
                "watchers": []
            },
            "D1-8": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "N",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "INDETERM",
                        "OPER_PHASE": "LINKUP",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D1-9": {
                "cmd": "sudo udldctl global",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "IS_ENABLED": "Y",
                        "IS_AGGR": "Y",
                        "MSG_INTV": "1",
                        "MULTIPLIER": "3",
                        "TIMEOUT_INTV": "3"
                    }
                ]
            },
            "D1-10": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"no udld aggressive\"",
                "watchers": []
            },
            "D1-11": {
                "cmd": "sudo udldctl global",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "IS_ENABLED": "Y",
                        "IS_AGGR": "N",
                        "MSG_INTV": "1",
                        "MULTIPLIER": "3",
                        "TIMEOUT_INTV": "3"
                    }
                ]
            },
            "D1-12": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "N",
                        "OPER_AGGR": "N",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "INDETERM",
                        "OPER_PHASE": "LINKUP",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D1-13": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface Ethernet 26\" -c \"udld aggressive\"",
                "watchers": []
            },
            "D1-14": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "INDETERM",
                        "OPER_PHASE": "LINKUP",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D1-15": {
                "cmd": "sudo udldctl global",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "IS_ENABLED": "Y",
                        "IS_AGGR": "N",
                        "MSG_INTV": "1",
                        "MULTIPLIER": "3",
                        "TIMEOUT_INTV": "3"
                    }
                ]
            },
            "D1-16": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface Ethernet 26\" -c \"no udld aggressive\"",
                "watchers": []
            },
            "D1-17": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "N",
                        "OPER_AGGR": "N",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "INDETERM",
                        "OPER_PHASE": "LINKUP",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D1-18": {
                "cmd": "sudo udldctl global",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "IS_ENABLED": "Y",
                        "IS_AGGR": "N",
                        "MSG_INTV": "1",
                        "MULTIPLIER": "3",
                        "TIMEOUT_INTV": "3"
                    }
                ]
            },
            "D1-19": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface Ethernet 26\" -c \"udld aggressive\"",
                "watchers": []
            },
            "D1-20": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "INDETERM",
                        "OPER_PHASE": "LINKUP",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D2-1": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"udld enable\"",
                "watchers": []
            },
            "D2-2": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface Ethernet 26\" -c \"udld enable\"",
                "watchers": []
            },
            "D2-3": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface Ethernet 26\" -c \"udld aggressive\"",
                "watchers": []
            },
            "D2-4": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "INDETERM",
                        "OPER_PHASE": "LINKUP",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D2-5": {
                "cmd": "sudo udldctl global",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "IS_ENABLED": "Y",
                        "IS_AGGR": "N",
                        "MSG_INTV": "1",
                        "MULTIPLIER": "3",
                        "TIMEOUT_INTV": "3"
                    }
                ]
            },
            "D1-21": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface Ethernet 26\" -c \"no shutdown\"",
                "watchers": []
            },
            "D1-22": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "INDETERM",
                        "OPER_PHASE": "LINKUP",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D2-6": {
                "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface Ethernet 26\" -c \"no shutdown\"",
                "watchers": []
            },
            "D2-7": {
                "cmd": "sudo sleep 2",
                "watchers": []
            },
            "D2-8": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "UP",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "BI-DIR",
                        "OPER_PHASE": "ADV",
                        "NBR_DEVID": "80A2.3526.0C5E",
                        "NBR_DEVID_LEN": "14",
                        "NBR_PORTID": "Ethernet26",
                        "NBR_PORTID_LEN": "10",
                        "NBR_DEV_NAME": "sonic",
                        "NBR_DEV_NAME_LEN": "6",
                        "NBR_TIMEOUT": "3",
                        "NBR_MSGTIME": "1"
                    }
                ]
            },
            "D1-23": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "UP",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "BI-DIR",
                        "OPER_PHASE": "ADV",
                        "NBR_DEVID": "80A2.3526.0E5E",
                        "NBR_DEVID_LEN": "14",
                        "NBR_PORTID": "Ethernet26",
                        "NBR_PORTID_LEN": "10",
                        "NBR_DEV_NAME": "Leaf2",
                        "NBR_DEV_NAME_LEN": "6",
                        "NBR_TIMEOUT": "3",
                        "NBR_MSGTIME": "1"
                    }
                ]
            }
        }
    },
    {
        "watch_lists/udld_init_aggr_to_shut.json": {
            "D1-1": {
                "cmd": "sudo show interface status Ethernet26",
                "watchers": [
                    {
                        "watch-key": "Interface"
                    },
                    {
                        "Interface": "Ethernet26",
                        "Oper": "up",
                        "Admin": "up"
                    }
                ]
            },
            "D2-1": {
                "cmd": "sudo show interface status Ethernet26",
                "watchers": [
                    {
                        "watch-key": "Interface"
                    },
                    {
                        "Interface": "Ethernet26",
                        "Oper": "up",
                        "Admin": "up"
                    }
                ]
            },
            "D1-2": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "UP",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "BI-DIR",
                        "OPER_PHASE": "ADV",
                        "NBR_DEVID": "80A2.3526.0E5E",
                        "NBR_DEVID_LEN": "14",
                        "NBR_PORTID": "Ethernet26",
                        "NBR_PORTID_LEN": "10",
                        "NBR_DEV_NAME": "Leaf2",
                        "NBR_DEV_NAME_LEN": "6",
                        "NBR_TIMEOUT": "3",
                        "NBR_MSGTIME": "1"
                    }
                ]
            },
            "D2-2": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "UP",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "BI-DIR",
                        "OPER_PHASE": "ADV",
                        "NBR_DEVID": "80A2.3526.0C5E",
                        "NBR_DEVID_LEN": "14",
                        "NBR_PORTID": "Ethernet26",
                        "NBR_PORTID_LEN": "10",
                        "NBR_DEV_NAME": "sonic",
                        "NBR_DEV_NAME_LEN": "6",
                        "NBR_TIMEOUT": "3",
                        "NBR_MSGTIME": "1"
                    }
                ]
            },
            "D1-3": {
                "cmd": "sudo udldctl rx_drop enable Ethernet26",
                "watchers": []
            },
            "D1-3_1": {
                "cmd": "sudo sleep 5",
                "watchers": []
            },
            "D1-4": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "SHUT",
                        "OPER_PHASE": "START",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D1-5": {
                "cmd": "sudo show interface status Ethernet26",
                "watchers": [
                    {
                        "watch-key": "Interface"
                    },
                    {
                        "Interface": "Ethernet26",
                        "Oper": "down",
                        "Admin": "down"
                    }
                ]
            },
            "D2-3": {
                "cmd": "sudo show interface status",
                "watchers": []
            },
            "D2-4": {
                "cmd": "sudo show interface status Ethernet26",
                "watchers": [
                    {
                        "watch-key": "Interface"
                    },
                    {
                        "Interface": "Ethernet26",
                        "Oper": "down",
                        "Admin": "up"
                    }
                ]
            },
            "D2-5": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "DOWN",
                        "OPER_OPCODE": "NA",
                        "OPER_UDLDSTATE": "INDETERM",
                        "OPER_PHASE": "START",
                        "NBR_DEVID": "",
                        "NBR_DEVID_LEN": "",
                        "NBR_PORTID": "",
                        "NBR_PORTID_LEN": "",
                        "NBR_DEV_NAME": "",
                        "NBR_DEV_NAME_LEN": "",
                        "NBR_TIMEOUT": "",
                        "NBR_MSGTIME": ""
                    }
                ]
            },
            "D1-6": {
                "cmd": "sudo udldctl rx_drop disable Ethernet26",
                "watchers": []
            },
            "D1-10": {
                "cmd": "sudo sleep 2",
                "watchers": []
            },
            "D1-7": {
                "cmd": "sudo config interface startup Ethernet26",
                "watchers": []
            },
            "D1-8": {
                "cmd": "sudo show interface status",
                "watchers": []
            },
            "D1-9": {
                "cmd": "sudo show interface status Ethernet26",
                "watchers": [
                    {
                        "watch-key": "Interface"
                    },
                    {
                        "Interface": "Ethernet26",
                        "Oper": "up",
                        "Admin": "up"
                    }
                ]
            },
            "D1-11": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "UP",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "BI-DIR",
                        "OPER_PHASE": "ADV",
                        "NBR_DEVID": "80A2.3526.0E5E",
                        "NBR_DEVID_LEN": "14",
                        "NBR_PORTID": "Ethernet26",
                        "NBR_PORTID_LEN": "10",
                        "NBR_DEV_NAME": "Leaf2",
                        "NBR_DEV_NAME_LEN": "6",
                        "NBR_TIMEOUT": "3",
                        "NBR_MSGTIME": "1"
                    }
                ]
            },
            "D2-6": {
                "cmd": "sudo show interface status Ethernet26",
                "watchers": [
                    {
                        "watch-key": "Interface"
                    },
                    {
                        "Interface": "Ethernet26",
                        "Oper": "up",
                        "Admin": "up"
                    }
                ]
            },
            "D2-7": {
                "cmd": "sudo udldctl port Ethernet26",
                "watchers": [
                    {
                        "watch-key": "NA"
                    },
                    {
                        "PORT": "Ethernet26",
                        "CFG_ENABLE": "Y",
                        "CFG_AGGR": "Y",
                        "OPER_AGGR": "Y",
                        "OPER_LNSTATE": "UP",
                        "OPER_OPCODE": "PROBE",
                        "OPER_UDLDSTATE": "BI-DIR",
                        "OPER_PHASE": "ADV",
                        "NBR_DEVID": "80A2.3526.0C5E",
                        "NBR_DEVID_LEN": "14",
                        "NBR_PORTID": "Ethernet26",
                        "NBR_PORTID_LEN": "10",
                        "NBR_DEV_NAME": "sonic",
                        "NBR_DEV_NAME_LEN": "6",
                        "NBR_TIMEOUT": "3",
                        "NBR_MSGTIME": "1"
                    }
                ]
            },
            "D1-12": {
                "cmd": "sudo mr_idp",
                "watchers": []
            }
        }
    }
]

"""***************UTILS**************"""

"""
py::
This file holds utility functions used across this project. viz. logger and output parsing.
"""

import glob
import logging
import typing as tp
import pdb
import textfsm
from tabulate import tabulate
import time
import re
import os
import copy
import json
import fcntl
import shutil
from datetime import datetime
import sys



# Create a custom logger
monitor_logger: logging.Logger = logging.getLogger(__name__)
replay_logger: logging.Logger = logging.getLogger(__name__)

g_pdb_set = False

empty_tuple: tp.Tuple = ()
sudo_offset: int = len('sudo ')

show_cmd_pattern = ('sudo udldctl',
                    'sudo show')
prompt_options = ('sonic#', ':~$')
g_runtime_variables = './rt_vars.txt'


def create_rt_vars_file(file_comment='Vars for testsuite ABC'):
    if os.stat(g_runtime_variables).st_size != 0:
        try:
            shutil.copy(g_runtime_variables, g_runtime_variables + datetime.now().__str__().replace(' ', '_'))
        except IOError as e:
            print("Unable to copy file. {}".format(e))
        except Exception as e:
            print("Unexpected error: ", sys.exc_info())

    line = '{'+'\n    "comment": "{}"\n'.format(file_comment)
    with open(g_runtime_variables, 'w') as f:
        f.writelines(line)


def monitor_logger_init():
    open('logs/monitor.log', 'w').close()

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler    = logging.FileHandler('logs/monitor.log')

    console_handler.setLevel(logging.DEBUG)  # change to appropriate level after dev complete
    file_handler.setLevel(logging.DEBUG)  # change it to appropriate level

    # Create formatter and add it to handlers
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    monitor_logger.addHandler(console_handler)
    monitor_logger.addHandler(file_handler)
    monitor_logger.setLevel(logging.DEBUG)


def replay_logger_init():
    open('logs/replay.log', 'w').close()

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler    = logging.FileHandler('logs/replay.log')

    console_handler.setLevel(logging.DEBUG)  # change to appropriate level after dev complete
    file_handler.setLevel(logging.DEBUG)  # change it to appropriate level

    # Create formatter and add it to handlers
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    replay_logger.addHandler(console_handler)
    replay_logger.addHandler(file_handler)
    replay_logger.setLevel(logging.DEBUG)

    """
    this is for root logger. if we didnt create separate monitor_logger.
    logging.basicConfig(level=logging.DEBUG
                        , format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                        , handlers=[console_handler, file_handler])
    """


def m_log_debug(msg: str) -> None:
    monitor_logger.debug(msg)


def m_log_info(msg: str) -> None:
    monitor_logger.info(msg)


def m_log_err(msg: str) -> None:
    if g_pdb_set:
        pdb.set_trace()
    monitor_logger.error(msg)


def m_log_excp(msg: str) -> None:
    monitor_logger.exception(msg)


def r_log_debug(msg: str) -> None:
    replay_logger.debug(msg)


def r_log_info(msg: str) -> None:
    replay_logger.info(msg)


def r_log_err(msg: str) -> None:
    if g_pdb_set:
        pdb.set_trace()
    replay_logger.error(msg)


def r_log_excp(msg: str) -> None:
    if g_pdb_set:
        pdb.set_trace()
    replay_logger.exception(msg)


def get_file_name(tc_name: str):
    if tc_name.find('watch_lists/') == -1:
        return 'watch_lists/'+tc_name+'.json'
    return tc_name+'.json'


def read_json_file_as_dict(wl_file):
    r_log_info('Read commands from : {}'.format(wl_file))
    wl = open(wl_file, 'r')
    try:
        p_dict = json.load(wl)
    except Exception:
        wl.close()
        r_log_err('File Not in proper JSON format, append } at end')
        with open(wl_file, 'a') as f:
            f.writelines('}')
            f.close()

        try:
            with open(wl_file, 'r') as wl:
                p_dict = json.load(wl)
        except Exception:
            r_log_err('failed to read {}'.format(wl_file))
            p_dict = None

    return p_dict


def read_int_in_range(prefix_str, min_int, max_int) -> int:
    """
    Read a number from terminal

    :param prefix_str: information printed to user
    :param min_int: range start
    :param max_int: range end
    :return: number
    """
    while True:
        try:
            val = int(input(prefix_str))
            if min_int <= val <= max_int:
                return val
        except Exception as e:
            m_log_excp('Please enter a valid int in range {}-{}'.format(min_int, max_int))
            m_log_excp('Received exception : {}'.format(e))
            continue
    pass


def replace_variables_to_dut_port_name(dut, str_t):
    """

    :param dut:
    :param str_t:
    :return:

    sort dut_ports[dut] by max key length to avoid substring overwrite problem
    ex:
    For 'D1': {'P1': 'Ethernet26', 'P1_1': 'Ethernet 26'},
    D1P1 and D1P1_1 are the variable names.
    when we search and replace in below given output it replaces interface D1P1_1 -> interface Ethernet26_1
        "D2-1": {
        "cmd": "sudo sonic-cli -c \"configure terminal\" -c \"interface D1P1_1\" -c \"no shutdown\"",
        "watchers": []
    }

    2019-12-12 14:54:17,367 - utils - INFO - D1-1 : executing : sudo sonic-cli -c "configure terminal" -c "interface Ethernet26_1" -c "no shutdown"

    So sort by longest key length at 1st index.

    """

    p_dict = copy.deepcopy(dut_ports[dut])
    # sorted(p_dict.items(), key=lambda s: len(s[0]), reverse=True)
    # we can also reverse sort them by length of key, but i believe just reverse should also do the trick.
    p_dict = dict(sorted(p_dict.items(), reverse=True))
    if str_t:
        for port in p_dict.keys():
            str_t = str_t.replace(dut + port, p_dict[port])
    return str_t


def replace_dut_port_names_to_variables(dut, str_t):
    if str_t:
        for port in dut_ports[dut].keys():
            str_t = str_t.replace(dut_ports[dut][port], dut + port)
    return str_t


def run_command(chan, cmd, wait_time=10):
    chan.send(cmd + '\n')

    # give sufficient time for command to execute and populate stdout.
    # else recv will return nothing in this call.
    # and data will be processed only in next call.
    time.sleep(1)

    buff_size = -1
    resp = ''
    while not resp.strip().endswith(prompt_options):
        try:
            chan.settimeout(wait_time)
            buff = chan.recv(buff_size).decode()
            resp += buff
        except Exception as e:
            m_log_excp('Exception : {}'.format(e))
            break

    return resp


def find_template_name_for_cmd(cmd):
    cmd = cmd.strip()
    if cmd.startswith('sudo '):
        cmd = cmd[len('sudo '):]

    match_tmpl = ''
    with open('cmd_template_map.json', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue

            p_cmd = line.split('->')[0].strip()

            if re.match(p_cmd, cmd):
                match_tmpl = line.split('->')[1].strip()
                break

    if not match_tmpl:
        m_log_debug('Template not found for cmd : {}'.format(cmd))
    else:
        m_log_debug('Cmd : {} => Template : {}'.format(p_cmd, match_tmpl))

    return match_tmpl


def process_show_output(cmd: str, stdout) -> tp.Tuple:
    """
    Execute the given 'cmd' and process the show output from stdout
    :param cmd: command to be executed on stdout
    :param stdout:
    :return:
     on error   -   None
     on success -   re_table, fsm_results

     re_table   : tabular format of template
     fsm_results: parsed output

    """

    cmd_file = find_template_name_for_cmd(cmd)
    if not cmd_file:
        m_log_debug('\n {}'.format(stdout))
        return -1, -1

    try:
        re_table = None
        for f in glob.glob('./templates/*.tmpl'):
            if cmd_file in f:
                template = open(f)
                re_table = textfsm.TextFSM(template)
                template.close()
        if not re_table:
            raise Exception('template file not found for {}'.format(cmd_file))

        fsm_results = re_table.ParseText(stdout)
        m_log_info('\n' + tabulate(fsm_results, headers=re_table.header, showindex='always', tablefmt='psql'))
    except Exception as e:
        m_log_err('Template parsing Failed')
        m_log_err('Received exception : {}'.format(e))
        m_log_err(stdout)
        return -1, -1
    return re_table, fsm_results


def add_runtime_variables(header, data, nrows, ncols):
    if nrows <= 0 or ncols <= 0:
        return

    new_vars = {}
    while True:
        var_name = input('variable name : ')
        if var_name == 'end':
            break

        var_name = 'MR_RT_VAR_' + var_name

        vars_str = ' '
        with open(g_runtime_variables, 'r') as f:
            lines = f.readlines()
            lines.append('}')
            curr_var_dict = json.loads(vars_str.join(lines))

        if var_name in curr_var_dict.keys():
            m_log_err('Variable name already exists, Enter new name')
            continue

        m_log_info('Variable is located @')
        row  = read_int_in_range('row : ', 0, nrows)
        col  = read_int_in_range('col : ', 0, ncols)

        col_name = header[col]

        import pdb
        pdb.set_trace()
        var_value = data[row][col]
        var_map_dict = {var_name: var_value}
        new_vars[str(row)+'_'+col_name] = var_name
        p_data = json.dumps(var_map_dict, indent=4)
        p_data = ',' + p_data[2:-1]

        with open(g_runtime_variables, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.writelines(p_data)
            fcntl.flock(f, fcntl.LOCK_UN)

        data[row][col] = var_name

    return data, new_vars



"""***************REPLAY&TEST**************"""

import typing
import re
from time import sleep
import paramiko.client as pc
from paramiko import AutoAddPolicy
import sys
import json
import datetime
from tabulate import tabulate
from copy import deepcopy


"""
global watch_list data
read watch_list.json into g_wl_data dictionary
Format::-
{dut_ip : {command, cmd_no, watchers}}
Ex::-
{
 "10.59.136.32": {
        "cmd": "sudo show vlan bri", 
        "cmd_no": 1, 
        "watchers": []
    }
}
"""
"""
ssh client object dictionary
each dut will have a client obj
"""
g_dut_clients: typing.Dict = {}


def r_syslog(opcode, line):
    if opcode == 'ERR':
        r_log_err(line)
    if opcode == 'INFO':
        r_log_info(line)


class DutClients:
    def __init__(self, dut_name: str, hostip: str, port: str, uname: str, pwd: str):
        self.uname = uname
        self.pwd = pwd
        self.hostip = hostip
        self.port = port
        self.dut_name = dut_name
        self.log_file = open('logs/' + dut_name + '.log', 'w')

        try:
            self.client = pc.SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(self.hostip, username=self.uname, password=self.pwd, timeout=10)
            transport = self.client.get_transport()
            self.chan = transport.open_session()
            self.chan.get_pty()
            self.chan.invoke_shell()

        except Exception as e:
            r_log_excp('Client connection Failed : {} {} {} {}'.format(hostip, port, uname, pwd))
            r_log_excp('Received exception : {}'.format(e))
            self.client.close()
            sys.exit(1)
            pass

    def syslog(self, op_code, line):
        self.log_file.writelines('\n{} : {:>15} :: {}'.format(datetime.datetime.now(), op_code, line))
        if op_code == 'ERR':
            r_log_err(line)
        if op_code == 'INFO':
            r_log_info(line)

    def abort_test(self):
        if g_pdb_set:
            import pdb
            pdb.set_trace()
        self.syslog('ERR', 'Aborting Test')
        sys.exit(1)

    def exec_cmd(self, tc_id, cmd, exp_op_list):
        self.syslog('CMD', cmd)

        if cmd.startswith('sudo sleep'):
            r1 = re.search(r'sudo sleep (?!$)([\d]*[.]?(?!$)[\d]*)', cmd)
            if len(r1.groups()) == 1:
                self.syslog('INFO', 'Sleep {}'.format(r1.groups()[0]))
                sleep(float(r1.groups()[0]))
                return

        try:
            stdout = run_command(self.chan, cmd)
            if 'error' in stdout:
                self.syslog('ERR', stdout)
        except Exception as e:
            r_log_excp('Command execution Failed')
            r_log_excp('Received exception : {}'.format(e))
            return

        if cmd.startswith(show_cmd_pattern):
            ret = process_show_output(cmd, stdout)
            if exp_op_list and ret is None:
                self.syslog('ERR', 'Failed to Process show output for {}'.format(cmd))
                return
            else:
                re_table, fsm_results = ret

            key_col_name = ''
            for exp_op in exp_op_list:
                if 'watch-key' in exp_op.keys():
                    key_col_name = exp_op['watch-key']
                    continue

                entry_w_key = {}
                actual_op = {}
                match_found = False
                for row in fsm_results:
                    actual_op = dict(zip(re_table.header, row))
                    if key_col_name == 'NA':
                        if exp_op.items() <= actual_op.items():
                            match_found = True
                            break
                    else:
                        if actual_op[key_col_name] == exp_op[key_col_name]:
                            entry_w_key = actual_op
                            # check if exp_op is a subset of actual op
                            if exp_op.items() <= actual_op.items():
                                match_found = True
                                break

                if not match_found:
                    if key_col_name != 'NA' and not entry_w_key:
                        self.syslog('ERR', 'Entry with key({}:{}) not Found'.format(key_col_name, exp_op[key_col_name]))
                    else:
                        if not entry_w_key:
                            p_dict = actual_op
                        else:
                            p_dict = entry_w_key

                        header = ['output']
                        diff_table = [['Exp'], ['Actual']]
                        for key in p_dict.keys():
                            header.append(key)
                            try:
                                diff_table[0].append(exp_op[key])
                            except Exception as KeyError:
                                diff_table[0].append('')
                            diff_table[1].append(p_dict[key])
                        self.syslog('ERR', ' Exp Vs Actual \n {}'.format(tabulate(diff_table, headers=header
                                                                                  , showindex='always'
                                                                                  , tablefmt='psql')))
                    self.syslog('ERR', 'Test {} FAILED'.format(tc_id))
                    self.abort_test()

            self.syslog('INFO', 'Test {} PASSED'.format(tc_id))
        pass


def start_automation(test_suite_name, tc_name='') -> None:
    """
    Read watch_list file and create all required ssh sessions.

    :return: None
    """
    for dut in dcon.keys():
        dc = DutClients(dut, dcon[dut]['ip'], '22', 'admin', 'broadcom')
        g_dut_clients[dcon[dut]['ip']] = dc

    if tc_name:
        wl_file = tc_name
        wl_dict = read_json_file_as_dict(wl_file)
        if wl_dict is not None:
            process_commands(wl_file, wl_dict)
        return

    with open(test_suite_name, 'r') as wl_suite:
        for wl_file in wl_suite.readlines():
            wl_file = wl_file.strip()
            if wl_file == '' or wl_file.startswith('#'):
                continue

            wl_dict = read_json_file_as_dict(wl_file)
            if wl_dict is not None:
                process_commands(wl_file, wl_dict)
    pass


def process_commands(wl_file, wl_dict) -> None:
    """
    Run automation from watch_list
    :return:
    """
    r_syslog('INFO', '#########################################')
    r_syslog('INFO', 'RUN Commands from {}'.format(wl_file[:-5]))
    r_syslog('INFO', '#########################################')

    rt_vars = read_json_file_as_dict(g_runtime_variables)
    if rt_vars is None:
        return

    for dut_cmd_no, w_val in wl_dict.items():
        dut = dut_cmd_no.split('-')[0]
        dut_ip = dcon[dut]['ip']
        dc = g_dut_clients[dut_ip]
        cmd: str = w_val['cmd']
        watchers: typing.List = w_val['watchers']

        if len(watchers) > 1:
            p_dict = watchers[1]

            for key, val in watchers[1].items():
                if val.startswith('MR_RT_VAR_'):
                    p_dict[key] = rt_vars[val]

        watchers = json.loads(replace_variables_to_dut_port_name(dut, json.dumps(watchers)))
        cmd      = replace_variables_to_dut_port_name(dut, cmd)
        r_syslog('INFO', '{} : executing : {}'.format(dut_cmd_no, cmd))

        dc.exec_cmd(dut_cmd_no, cmd, watchers)

    pass


def idp_start_automation():
    """
    Read watch_list file and create all required ssh sessions.

    :return: None
    """
    for dut in dcon.keys():
        dc = DutClients(dut, dcon[dut]['ip'], '22', 'admin', 'broadcom')
        g_dut_clients[dcon[dut]['ip']] = dc
    pass


"""***************MAIN**************"""

if __name__== "__main__":
    replay_logger_init()
    for dut in dcon.keys():
        dc = DutClients(dut, dcon[dut]["ip"], "22", "admin", "broadcom")
        g_dut_clients[dcon[dut]["ip"]] = dc
    for tc_wl_dict in g_wl_tc_dict_list:
        tc_name, wl_dict = tc_wl_dict.popitem()
        process_commands(tc_name, wl_dict)
