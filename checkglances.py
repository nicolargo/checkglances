#!/usr/bin/env python
#
# CheckGlances
# Get stats from a Glances server
#
# Copyright (C) Nicolargo 2012 <nicolas@nicolargo.com>
#
# This script is distributed
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This script is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.";
#

__appname__ = 'CheckGlances'
__version__ = "0.5"
__author__ = "Nicolas Hennion <nicolas@nicolargo.com>"
__licence__ = "LGPL"

# Import libs
#############

import sys
import time
import getopt
import xmlrpclib
import json
import gettext
gettext.install(__appname__)

# Classes
#########

class nagiospluginskeleton(object):
    """
    A top level skeleton for a Nagios plugin
    Do NOT use this class
    USE the child class nagiosplugin to define your plugin (see below)
    """

    # http://nagiosplug.sourceforge.net/developer-guidelines.html
    return_codes = {'OK': 0,
                    'WARNING': 1,
                    'CRITICAL': 2,
                    'UNKNOWN': 3 }

    def __init__(self):
        """
        Init the class
        """
        self.verbose = False


    def version(self):
        """
        Returns the plugin syntax
        """
        print(_("%s version %s") % (__appname__, __version__))


    def syntax(self):
        """
        Returns the plugin syntax
        """
        print(_("Syntax: %s -Vhv -H <host> [-p <port>] [-P <password>] -s <stat> [-e <param>] -w <warning> -c <critical>") % (format(sys.argv[0])))
        print("")
        print("        "+_("-V             Display version and exit"))
        print("        "+_("-h             Display syntax and exit"))
        print("        "+_("-v             Set verbose mode on (default is off)"))
        print("        "+_("-H <hosts>     Glances server hostname or IP address"))
        print("        "+_("-w <warning>   Warning threshold"))
        print("        "+_("-c <critical>  Critical threshold"))


    def setverbose(self, verbose = True):
        self.verbose = verbose


    def log(self, message):
        if (self.verbose):
            print(message)


    def exit(self, code):
        """
        The end...
        """
        sys.exit(self.return_codes[code])


class nagiosplugin(nagiospluginskeleton):
    """
    These class defines your Nagios Plugin
    """

    statslist = ('system', 'uptime', 'cpu', 'load', 'mem', 'swap', 'process', 'net', 'diskio', 'fs')
    statsparamslist = ( 'net' , 'diskio' , 'fs')

    def syntax(self):
        # Display the standard syntax
        super(nagiosplugin, self).syntax()
        # Display the specific syntax
        print("        "+_("-p <port>      Glances server TCP port (default 61209)"))
        print("        "+_("-P <password>  Glances server password (optional)"))
        print("        "+_("-s <stat>      Select stat to grab: %s")
                                            % ", ".join(self.statslist))
        print("        "+_("-e <param>     Extended parameter for stat: %s")
                                            % ", ".join(self.statsparamslist))


    # def methodexist(self, server, method):
    #     # Check if a method exist on the RCP server
    #     # return method in server.system.listMethods()
    #     return True


    def check(self, host, warning, critical, **args):
        """
        INPUT
         host: hostname or IP address to check
         warning: warning value
         critical: critical value
         args: optional arguments
        OUTPUT
         One line text message on STDOUT
         Return code
            self.exit('OK') if check is OK
            self.exit('WARNING') if check is WARNING
            self.exit('CRITICAL') if check is WARNING
            self.exit('UNKNOWN') if check ERROR
        """

        # Connect to the Glances server
        self.log(_("Check host: %s") % host)
        if (args['password'] != ''):
            gs = xmlrpclib.ServerProxy('http://%s:%s@%s:%d' % \
                ('glances', args['password'], host, int(args['port'])))
        else:
            gs = xmlrpclib.ServerProxy('http://%s:%d' % (host, int(args['port'])))
        self.log(_("Others args: %s") % args)

        # Test RCP server connection
        remote_system = None
        try:
            # getSystem() was born in the 1.5.2 version of Glances
            remote_system = gs.getSystem()
            self.log(_("Info: remote system is: %s") % remote_system)
        except xmlrpclib.Fault as err:
            # getSystem method unknown ?... mmhhh...
            self.log(_("Warning: %s works better with Glances server 1.5.2 or higher") % __appname__)
            pass
        except:
            print(_("Connection to Glances server failed"))
            self.exit('UNKNOWN')

        # DEBUG
        # print gs.system.listMethods()
        #~ print eval(gs.getSystem())
        # END DEBUG

        if (args['stat'] == "system"):

            # Get remote system information
            try:
                # {"platform": "32bit", "os_name": "Windows", "hr_name": "Windows 7 SP1 32bit", "hostname": "sim-vm", "os_version": "7 SP1"}
                remote_system = json.loads(remote_system)
                print(_("%s: %s (%s - %s - %s)") % (
                    remote_system["hostname"],
                    remote_system["hr_name"],
                    remote_system["os_name"],
                    remote_system["os_version"],
                    remote_system["platform"]
                ))
            except xmlrpclib.Fault as err:
                print(_("Bad formed Glances server response: %s") % remote_system)
                self.exit('UNKNOWN')

            self.exit('OK')


        elif (args['stat'] == "uptime"):

            # Get and eval uptime stat
            try:
                uptime = json.loads(gs.getUptime())
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getUptim"))
                self.exit('UNKNOWN')
            else:
                self.log(_("Uptime: %s") % uptime)

            if not uptime:
                print(_("No uptime information available from host"))
                self.exit('UNKNOWN')

            uptime_s = time.strptime(uptime, "%H:%M:%S")
            self.log(_("Uptime: %s") % uptime_s)

            if (warning is None): warning = 15 * 60
            if (critical is None): critical = 5 * 60
            seconds = uptime_s.tm_hour * 3600 + uptime_s.tm_min * 60 + uptime_s.tm_sec

            # Plugin output
            checked_message = _("System uptime: %s (%d seconds)") % (uptime, seconds)
            # Performance data
            checked_message += _(" | 'uptime'=%ds;;;%s;%s") % (seconds, warning, critical)

            # Display the message
            self.log(_("Warning threshold: %s" % warning))
            self.log(_("Critical threshold: %s" % critical))
            print(checked_message)

            # Return code
            if (seconds < int(critical)):
                self.exit('CRITICAL')
            elif (seconds < int(warning)):
                self.exit('WARNING')
            else:
                self.exit('OK')


        elif (args['stat'] == "cpu"):

            # Get and eval CPU stat

            try:
                cpu = json.loads(gs.getCpu())
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getCpu"))
                self.exit('UNKNOWN')
            else:
                self.log(cpu)
            #~ print cpu
            #~ If user|kernel|nice CPU is > 70%, then status is set to "WARNING".
            #~ If user|kernel|nice CPU is > 90%, then status is set to "CRITICAL".
            if (warning is None): warning = 70
            if (critical is None): critical = 90
            checked_value = 100 - cpu['idle']
            # Plugin output
            checked_message = _("CPU consumption: %.2f%%") % checked_value
            # Performance data
            checked_message += _(" | 'percent'=%.2f;0;100;%s;%s") % (checked_value, warning, critical)
            for key in cpu:
                checked_message += " '%s'=%.2f" % (key, cpu[key])


        elif (args['stat'] == "load"):

            # Get and eval CORE and LOAD stat

            try:
                # Glances v2
                core = eval(gs.getCore(), {'null': None})["log"]
            except KeyError:
                # Glances v1
                core = eval(gs.getCore(), {'null': None})
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getLoad"))
                self.exit('UNKNOWN')
            else:
                self.log(_("Core: %d") % core)
            try:
                load = eval(gs.getLoad(), {'null': None})
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getLoad"))
                self.exit('UNKNOWN')
            else:
                self.log(_("Load: %s") % load)

            if not load:
                print(_("No load information available from host"))
                self.exit('UNKNOWN')

            #~ If average load is > 1*Core, then status is set to "WARNING".
            #~ If average load is > 5*Core, then status is set to "CRITICAL".
            if (warning is None): warning = 1
            if (critical is None): critical = 5
            warning *= core
            critical *= core
            checked_value = load['min5']
            # Plugin output
            checked_message = _("LOAD last 5 minutes: %.2f") % checked_value
            # Performance data
            checked_message += _(" |")
            for key in load:
                if (key == "min5"):
                    checked_message += " '%s'=%.2f;%s;%s" % (key, load[key], warning, critical)
                else:
                    checked_message += " '%s'=%.2f" % (key, load[key])


        elif (args['stat'] == "mem"):

            # Get and eval MEM stat
            try:
                mem = json.loads(gs.getMem())
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getMem"))
                self.exit('UNKNOWN')
            else:
                self.log(mem)
            #~ If memory is > 70%, then status is set to "WARNING".
            #~ If memory is > 90%, then status is set to "CRITICAL"
            if (warning is None): warning = 70
            if (critical is None): critical = 90
            checked_value = mem['percent']
            # Plugin output
            checked_message = _("MEM consumption: %.2f%%") % checked_value
            # Performance data
            checked_message += _(" |")
            for key in mem:
                if (key == "min5"):
                    checked_message += " '%s'=%.2f;%s;%s" % (key, mem[key], warning, critical)
                else:
                    checked_message += " '%s'=%.2f" % (key, mem[key])


        elif (args['stat'] == "swap"):

            # Get and eval MEM stat
            try:
                swap = json.loads(gs.getMemSwap())
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getMemSwap"))
                self.exit('UNKNOWN')
            else:
                self.log(swap)
            #~ If memory is > 70%, then status is set to "WARNING".
            #~ If memory is > 90%, then status is set to "CRITICAL"
            if (warning is None): warning = 70
            if (critical is None): critical = 90
            checked_value = swap['percent']
            # Plugin output
            checked_message = _("SWAP consumption: %.2f%%") % checked_value
            # Performance data
            checked_message += _(" |")
            for key in swap:
                if (key == "min5"):
                    checked_message += " '%s'=%.2f;%s;%s" % (key, swap[key], warning, critical)
                else:
                    checked_message += " '%s'=%.2f" % (key, swap[key])


        elif (args['stat'] == "process"):

            # Get and eval Process stat
            try:
                process = json.loads(gs.getProcessCount())
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getProcessCount"))
                self.exit('UNKNOWN')
            else:
                self.log(process)
            #~ If running process is > 50, then status is set to "WARNING".
            #~ If running process is > 100, then status is set to "CRITICAL"
            if (warning is None): warning = 50
            if (critical is None): critical = 100
            checked_value = process['running']
            # Plugin output
            checked_message = _("Running processes: %d") % checked_value
            # Performance data
            checked_message += _(" |")
            for key in process:
                if (key == "min5"):
                    checked_message += " '%s'=%.2f;%s;%s" % (key, process[key], warning, critical)
                else:
                    checked_message += " '%s'=%.2f" % (key, process[key])


        elif (args['stat'] == "net"):

            # Get and eval Network stat
            try:
                net = json.loads(gs.getNetwork())
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getNetwork"))
                self.exit('UNKNOWN')
            else:
                self.log(net)
            #~ If net[param] > 60 Mbps, then status is set to "WARNING".
            #~ If net[param] > 80 Mbps, then status is set to "CRITICAL"
            # Values are in Kbyte/second
            if (warning is None): warning = 7500000
            if (critical is None): critical = 10000000
            checked_value = -1
            for interface in net:
                if interface['interface_name'] == args['statparam']:
                    checked_value = max(interface["tx"], interface["rx"])
                    break
            if (checked_value == -1):
                print(_("Unknown network interface: %s") % args['statparam'])
                self.exit('UNKNOWN')
            # Plugin output
            checked_message = _("Network rate: %d") % checked_value
            # Performance data
            checked_message += _(" |")
            for key in interface:
                checked_message += " '%s'=%s" % (key, interface[key])


        elif (args['stat'] == "diskio"):

            # Get and eval Network stat

            try:
                diskio = json.loads(gs.getDiskIO())
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getDiskIO"))
                self.exit('UNKNOWN')
            else:
                self.log(diskio)

            #~ If diskio[param] > 30 Mbytes/sec, then status is set to "WARNING".
            #~ If diskio[param] > 40 MBytes/sec, then status is set to "CRITICAL"
            if (warning is None): warning = 30000000
            if (critical is None): critical = 40000000
            checked_value = -1
            for disk in diskio:
                if disk['disk_name'] == args['statparam']:
                    # checked_value = max(disk["read_bytes"], disk["write_bytes"])
                    checked_value = disk["read_bytes"]
                    break
            if (checked_value == -1):
                print(_("Unknown disk: %s") % args['statparam'])
                self.exit('UNKNOWN')
            # Plugin output
            checked_message = _("Disk IO: %d") % checked_value
            # Performance data
            checked_message += _(" |")
            for key in disk:
                if (key == "read_bytes"):
                    checked_message += " '%s'=%.2f;%s;%s" % (key, disk[key], warning, critical)
                elif (key == "write_bytes"):
                    checked_message += " '%s'=%.2f" % (key, disk[key])
                elif (key == "time_since_update"):
                    checked_message += " '%s'=%.2f" % (key, disk[key])


        elif (args['stat'] == "fs"):

            # Get and eval Network stat

            try:
                fs = json.loads(gs.getFs())
            except xmlrpclib.Fault as err:
                print(_("Can not run the Glances method: getFs"))
                self.exit('UNKNOWN')
            else:
                self.log(fs)
            #~ If fs[param] > %, then status is set to "WARNING".
            #~ If fs[param] > %, then status is set to "CRITICAL"
            if (warning is None): warning = 70
            if (critical is None): critical = 90
            checked_value = -1
            for disk in fs:
                mnt_point = args['statparam']
                # If the FS looks like it is a Windows drive, automatically add the Windows slash
                if not args['statparam'].startswith("/") and not args['statparam'].endswith("\\"):
                        mnt_point = args['statparam'].replace(":",":\\")
                if disk['mnt_point'] == mnt_point:
                    checked_value = disk["percent"]
                    break
            if (checked_value == -1):
                print(_("Unknown mounting point: %s") % args['statparam'])
                self.exit('UNKNOWN')
            # Plugin output
            checked_message = _("FS using space: %d%%") % checked_value
            # Performance data
            checked_message += _(" |")
            for key in disk:
                checked_message += " '%s'=%s" % (key, disk[key])
            checked_message += " 'pctfree'=%s%%;%s;%s;0;100" % (checked_value,warning,critical)


        else:

            # Else...

            print(_("Unknown stat: %s") % args['stat'])
            self.exit('UNKNOWN')

        # Display the message
        self.log(_("Warning threshold: %s" % warning))
        self.log(_("Critical threshold: %s" % critical))
        print(checked_message)

        # Return code
        if (checked_value < warning):
            self.exit('OK')
        elif (checked_value < critical):
            self.exit('WARNING')
        elif (checked_value < critical):
            self.exit('CRITICAL')


# Main function
###############

def main():

    # Create an instance of the your plugin
    plugin = nagiosplugin()

    # Manage command line arguments
    if len(sys.argv) < 2:
        plugin.syntax()
        plugin.exit('UNKNOWN')

    try:
        # Add optional tag definition here
        # ...
        opts, args = getopt.getopt(sys.argv[1:], "VhvH:p:P:w:c:s:e:")
    except getopt.GetoptError, err:
        plugin.syntax()
        plugin.exit('UNKNOWN')

    # Default parameters
    warning = None
    critical = None
    port = 61209
    password = ""
    statparam = ""

    for opt, arg in opts:
        # Standard tag definition
        if opt in ("-V", "--version"):
            plugin.version()
            plugin.exit('OK')
        elif opt in ("-h", "--help"):
            plugin.syntax()
            plugin.exit('OK')
        elif opt in ("-v", "--verbose"):
            plugin.setverbose()
            print(_("Verbose mode ON"))
        elif opt in ("-H", "--hostname"):
            host = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-P", "--password"):
            password = arg
        elif opt in ("-w", "--warning"):
            warning = arg
        elif opt in ("-c", "--critical"):
            critical = arg
        elif opt in ("-s", "--stat"):
            stat = arg
        elif opt in ("-e", "--statparam"):
            statparam = arg
        else:
            # Tag is UNKNOW
            plugin.syntax()
            plugin.exit('UNKNOWN')

    # Check args
    try:
        host
    except:
        print(_("You need to specify an hostname or IP address"))
        plugin.exit('UNKNOWN')
    try:
        stat
    except:
        print(_("You need to specify the stat to grab (use the -s tag)"))
        plugin.exit('UNKNOWN')
    else:
        if stat not in plugin.statslist:
            print(_("Use -s with value in %s") % ", ".join(plugin.statslist))
            plugin.exit('UNKNOWN')
        if (stat == "net") and (statparam == ""):
            print(_("You need to specify the interface name with -e <interface>"))
            plugin.exit('UNKNOWN')
        if (stat == "diskio") and (statparam == ""):
            print(_("You need to specify the disk name with -e <disk>"))
            plugin.exit('UNKNOWN')
        if (stat == "fs") and (statparam == ""):
            print(_("You need to specify the mounting point with -e <fs>"))
            plugin.exit('UNKNOWN')


    # Do the check
    plugin.check(host, warning, critical, port = port, password = password, \
                 stat = stat, statparam = statparam)


# Main program
##############

if __name__ == "__main__":
    main()
