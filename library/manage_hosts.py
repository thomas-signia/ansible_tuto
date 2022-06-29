#!/usr/bin/python
# -*- coding: utf-8 -*-
from ansible.module_utils.basic import *
import os

def main():

    module_args = {"entries": {"default": [], "type": "list"}}
    module = AnsibleModule(argument_spec=module_args)

    if any(('ip' not in entry.keys() or 'names' not in entry.keys()) for entry in module.params['entries']):
        module.fail_json(msg="All entries should have both an 'ip' key and a 'names' key.", changed=False)

    if os.path.exists("/etc/hosts"):    # Linux
        etc_hosts_path = "/etc/hosts"
    else:
        etc_hosts_path = os.path.join("C:" + os.sep, "Windows", "System32", "Drivers", "etc", "hosts")    # Windows

    with open(etc_hosts_path, 'r') as fin:
        existing_lines = fin.read().splitlines()
    hosts = {line.split(' ')[0]: set(line.split(' ')[1:]) for line in existing_lines}
    old_hosts = hosts.copy()

    for entry in module.params['entries']:
        if entry['ip'] in hosts:
            hosts[entry['ip']] = hosts[entry['ip']].union(set(entry['names']))
        else:
            hosts[entry['ip']] = set(entry['names'])
    changed = hosts != old_hosts
        
    host_string = ""
    for ip, names in hosts.items():
        host_string += ip + " " + " ".join(names) + "\n"
    
    with open(etc_hosts_path, 'w') as fout:
        fout.write(host_string)

    response = {"result" : "OK"}
    module.exit_json(changed=changed, meta=response)

if __name__ == '__main__':
    main()