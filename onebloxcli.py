__author__ = 'veeru'
"""Simple Sharsrv client to perform administrative actions.
"""

import json
import logging
import sys

from erasefs import cls_erasefs
from findmop import cls_findmop
from runcmd import cls_runcmd
from copy import cls_copy
from share import cls_share
logging.basicConfig(format="%(message)s")
logger = logging.getLogger(__name__)


class onebloxcli(cls_erasefs, cls_findmop, cls_runcmd, cls_copy, cls_share):
    ssh_key = "oneblox-ssh-key"
    def onebloxcli(self):
        self.ssh_key = "oneblox-ssh-key"

    def erasefs(self,  ip_addrs, cluster_name):
        #obj_erasefs = cls_erasefs()
        self.cli_erasefs(ip_addrs, cluster_name, self.ssh_key)
        return

    def runcmd(self,  ip_addrs,  cmds_list):
        self.cli_runcmd(ip_addrs, cmds_list, self.ssh_key)
        return

    def find_mop(self,  node_ip_list):
        mop_ip = self.cli_findmop(node_ip_list, self.ssh_key)
        print " mop ip", mop_ip

    def copy_file(self,  node_ip_list,  source_path,  dest_path):
        mop_ip = self.cli_findmop(node_ip_list, self.ssh_key)
        print " Mop node ", mop_ip
        self.cli_copy(mop_ip, source_path, dest_path, self.ssh_key)


    def create_share(self, node_ip_list, share_type, share_name, share_count=1):
        mop_ip = self.cli_findmop(node_ip_list, self.ssh_key)
        self.cli_share_op(mop_ip, "create", share_type, share_name, self.ssh_key, share_count)

    def delete_share(self, node_ip_list, share_type, share_name, share_count=1):
        mop_ip = self.cli_findmop(node_ip_list, self.ssh_key)
        self.cli_share_op(mop_ip, "remove", share_type, share_name, self.ssh_key, share_count)


CLIENT_CMDS = {
    'onebloxcli': {
        'erasefs': {
            'help': '<IP(s)> Erase file system for all specified nodes',
            'method': onebloxcli.erasefs,
            'args': [str, str]
        },
        'runcmd': {
            'help': '<IP(s)> <Command List> Execute the commands on specifed IPs',
            'method': onebloxcli.runcmd,
            'args': [str, str]
        },
        'mop': {
            'help': '<IP(s)> Find the MOP node from the specifed IPs',
            'method': onebloxcli.find_mop,
            'args': [str]
        },
        'copy': {
            'help': '<IP(s)> <Source path > <Destnation share name> '
                    'Copy file to oneblox share',
            'method': onebloxcli.copy_file,
            'args': [str, str, str]
        },
        'createshare': {
            'help': '<IP>  <smb/nfs> <Share Name > Create specifed number of shares',
            'method': onebloxcli.create_share,
            'args': [str, str, str, str]
        },
        'deleteshare': {
            'help': '<IP> <Share Name> Delete specifed number of shares',
            'method': onebloxcli.delete_share,
            'args': [str, str, str, str]
        },
    }
}

class oneblox_interface(onebloxcli):

    def pretty_print_json(self, json_input):
        return json.dumps(json_input, sort_keys=True, indent=4, separators=(',', ': '))

    def print_client_help(self):
        for cmd, subcmds in CLIENT_CMDS.items():
            for subcmd, info in subcmds.items():
                print '\t%-15s%-15s: %s' % (cmd, subcmd, CLIENT_CMDS[cmd][subcmd]['help'])

    def parse_cmd_args(self, cmd_args, cmd_argtype):
        args = []
        print cmd_args, cmd_argtype, len(cmd_args)
        for argnum in range(len(cmd_argtype)):
            # Cast argnum into expected argtype
            arg = cmd_argtype[argnum](cmd_args[argnum])
            args.append(arg)
        return args

    def run_client_cmd(self, client, cmd):
        if (len(cmd) < 2 or
            cmd[1] not in CLIENT_CMDS or
            cmd[2] not in CLIENT_CMDS[cmd[1]]):
            print "Unknown command: %s" % input
            self.print_client_help()
            return

        cmd_def = CLIENT_CMDS[cmd[1]][cmd[2]]
        if cmd_def['args'] is not None:
            cmd_args = self.parse_cmd_args(cmd[3:], cmd_def['args'])
            if cmd_args is None:
                print "Error Parsing args for command: %s" % input
                return
            result = cmd_def['method'](client, *cmd_args)
        else:
            result = cmd_def['method']()

        if result is None:
            return
        elif isinstance(result, str):
            print result
        else:
            output = self.pretty_print_json(result)
            print output

def main():
    cli_cmd = oneblox_interface()
    if len(sys.argv) < 3:
        print("Invalid arguments.....!!!")
        print("USAGE : ")
        cli_cmd.print_client_help()
        sys.exit()
    cmd_string = ""
    for item in sys.argv:
        cmd_string = cmd_string+item+" "
    cli_cmd.run_client_cmd(cli_cmd, sys.argv)
    #testShare.run_client_cmd(testShare, "onebloxcli erasefs --ip 1.1.1.1,2.2.2.2 --cluster ONEBLOX")
    #testShare.run_client_cmd(testShare, "onebloxcli runcmd --ip 1.1.1.1,2.2.2.2,3.3.3.3 --cmd 'erase -l,dir,mkdir'")
    #testShare.run_client_cmd(testShare, "onebloxcli mop --ip 1.1.1.1,2.2.2.2,3.3.3.3")
    #testShare.run_client_cmd(testShare, "onebloxcli createshare --ip 1.1.1.1 --sharename myshare")
    #testShare.run_client_cmd(testShare, "onebloxcli deleteshare --ip 1.1.1.1 --sharename myshare")
    #testShare.print_client_help()

if __name__ == "__main__":
    sys.exit(main())

