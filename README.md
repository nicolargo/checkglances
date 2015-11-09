=========================================================
A Nagios|Shinken plugin to grab stats on a Glances server
=========================================================

![screenshot](https://github.com/nicolargo/checkglances/raw/master/doc/checkglances.png)

## What is it ?

CheckGlances is a Nagios plugin. It can grab stat on a Glances server using a XML RCP over HTTP link.

Glances server can be ran on GNU/Linux, BSD, Mac OS and Windows operating system.

1) Start [Glances](http://nicolargo.github.com/glances/) server on yours hosts

2) Configure our Nagios|Shinken server with the CheckGlances plugin

3) Enjoy...

## Be aware...

Use checkglances v0.4 for Glances 1.x server
Or checkglances v0.5 or higher for Glances 2.x (or higher)

## CLI Examples

CPU

    $ ./checkglances.py -H localhost -s cpu
    CPU consumption: 2.96% | 'percent'=2.96 'kernel'=0.73 'iowait'=0.20 'idle'=97.04 'user'=1.89 'irq'=0.00 'nice'=0.00

LOAD

    $ ./checkglances.py -H localhost -s load
    LOAD last 5 minutes: 0.22% | 'min1'=0.13 'min5'=0.22 'min15'=0.29

MEM

    $ ./checkglances.py -H localhost -s mem
    MEM consumption: 59.50% | 'used'=3411509248.00 'cache'=1071792128.00 'total'=3934547968.00 'percent'=59.50 'free'=523038720.00

SWAP

    $ ./checkglances.py -H localhost -s swap
    SWAP consumption: 3.70% | 'used'=150159360.00 'total'=4080005120.00 'percent'=3.70 'free'=3929845760.00

PROCESS

    $ ./checkglances.py -H localhost -s process
    Running processes: 1 | 'running'=1 'total'=143 'sleeping'=142

NETWORK

    $ ./checkglances.py -H localhost -s net -e eth0
    Network rate: 5479658 | 'interface_name'=eth0 'rx'=327514 'tx'=5479658

FILE SYSTEM

    $ ./checkglances.py -H localhost -s fs -e /
    FS using space: 8% | 'mnt_point'=/ 'used'=22371450880 'device_name'=/dev/sda2 'avail'=910404046848 'fs_type'=ext4 'size'=982693486592

Also implemented: getDiskIO, uptime, system

## How to configure Nagios ?

First of all, copy the checkglances.py file to your Nagios plugin folder.

Then enter the new section on your commands.cfg file:

    define command{
        command_name checkglances
        command_line $USER1$/checkglances.py -H $HOSTADDRESS$ -s $ARG1$ -w $ARG2$ -c $ARG3$
    }

    define command{
        command_name checkglanceswithparam
        command_line $USER1$/checkglances.py -H $HOSTADDRESS$ -s $ARG1$ -e $ARG2$-w $ARG3$ -c $ARG4$
    }
    
Configure a new service for your host (where Glances server is up and running):

    define service {
        use generic-service
        host_name myhost
        service_description CPU
        check_command checkglances!cpu!70!90
    }

    define service {
        use generic-service
        host_name myhost
        service_description LOAD
        check_command checkglances!load!1!5
    }

    define service {
        use generic-service
        host_name myhost
        service_description MEM
        check_command checkglances!mem!70!90
    }

    define service {
        use generic-service
        host_name myhost
        service_description SWAP
        check_command checkglances!swap!70!90
    }

    define service {
        use generic-service
        host_name myhost
        service_description PROCESS
        check_command checkglances!process!30!100
    }

    define service {
        use generic-service
        host_name myhost
        service_description NETWORK eth0
        check_command checkglanceswithparam!net!eth0!7500000!10000000
    }

    define service {
        use generic-service
        host_name myhost
        service_description FILESYSTEM /
        check_command checkglanceswithparam!fs!/!70!90
    }

## Coming soon...

Disk IO
