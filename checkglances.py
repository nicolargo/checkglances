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
__version__ = "0.1b"
__author__ = "Nicolas Hennion <nicolas@nicolargo.com>"
__licence__ = "LGPL"

# Import libs
#############

import sys
import getopt
import xmlrpclib
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
        print(_("Syntax: %s -Vhv -H <host> -w <warning> -c <critical>") % (format(sys.argv[0])))
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

    statslist = ('cpu', 'load', 'mem', 'swap')

    def syntax(self):
        # Display the standard syntax
        super(nagiosplugin, self).syntax()
        # Display the specific syntax
        print("        "+_("-s <port>      Glances server TCP port (default 61209)")) 
        print("        "+_("-s <stat>      Select stat to grab: %s") 
                                            % ", ".join(self.statslist))


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
        gs = xmlrpclib.ServerProxy('http://%s:%d' % (host, int(args['port'])))
        
        self.log(_("Others args: %s") % args)
        if (args['stat'] == "cpu"):
            # Get and eval CPU stat
            cpu = eval(gs.getCpu())
            #~ If user|kernel|nice CPU is > 70%, then status is set to "WARNING".
            #~ If user|kernel|nice CPU is > 90%, then status is set to "CRITICAL".
            if (warning is None): warning = 70
            if (critical is None): critical = 90                
            checked_value = 100 - cpu['idle']
            # Plugin output
            checked_message = _("CPU consumption: %.2f%%") % checked_value
            # Performance data
            checked_message += _(" | 'percent'=%.2f") % checked_value
            for key in cpu:
                checked_message += " '%s'=%.2f" % (key, cpu[key])
        elif (args['stat'] == "load"):
            # Get and eval LOAD stat
            load = eval(gs.getLoad())
            #~ core = eval(gs.getCore())
            core = 1
            #~ If average load is > 1*Core, then status is set to "WARNING".
            #~ If average load is > 5*Core, then status is set to "CRITICAL".
            if (warning is None): warning = core
            if (critical is None): critical = 5*core 
            checked_value = load['min5']
            # Plugin output
            checked_message = _("LOAD last 5 minutes: %.2f%%") % checked_value
            # Performance data
            checked_message += _(" |")
            for key in load:
                checked_message += " '%s'=%.2f" % (key, load[key])
        elif (args['stat'] == "mem"):
            # Get and eval MEM stat
            mem = eval(gs.getMem())
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
                checked_message += " '%s'=%.2f" % (key, mem[key])
        elif (args['stat'] == "swap"):
            # Get and eval MEM stat
            swap = eval(gs.getMemSwap())
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
                checked_message += " '%s'=%.2f" % (key, swap[key])
        else:
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
        opts, args = getopt.getopt(sys.argv[1:], "VhvH:p:w:c:s:")
    except getopt.GetoptError, err:
        plugin.syntax()
        plugin.exit('UNKNOWN')

    # Default parameters
    warning = None
    critical = None
    port = 61209
    
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
        elif opt in ("-w", "--warning"):
            warning = arg
        elif opt in ("-c", "--critical"):
            critical = arg
        elif opt in ("-s", "--stat"):
            stat = arg
        else:
            # Tag is UNKNOW
            plugin.syntax()
            plugin.exit('UNKNOWN')

    # Check args
    try:
        host
    except:
        print(_("Need to specified an hostname or IP address"))
        plugin.exit('UNKNOWN')
    try:
        stat
    except:
        print(_("Need to specified the stat to grab (use the -s tag)"))        
        plugin.exit('UNKNOWN')
    else:
        if stat not in plugin.statslist:
            print(_("Use -s with value in %s") % ", ".join(plugin.statslist))        
            plugin.exit('UNKNOWN')
        
    # Do the check
    plugin.check(host, warning, critical, port = port, stat = stat)


# Main program
##############

if __name__ == "__main__":
    main()
