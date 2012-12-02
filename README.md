## A Nagios|Shinken plugin to grab stats on a Glances server

1) Start [Glances](http://nicolargo.github.com/glances/) server on yours hosts

2) Configure Nagios|Shinken with the checkglances plugin

3) Enjoy...

# Examples:

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

