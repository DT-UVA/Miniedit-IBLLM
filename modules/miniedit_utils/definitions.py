from mininet.node import Controller, RemoteController, OVSController, CPULimitedHost, Host, NOX
from mininet.topo import SingleSwitchTopo, LinearTopo, SingleSwitchReversedTopo
from mininet.topolib import TreeTopo
from mininet.link import TCLink, Link
from mininet.net import VERSION
from mininet.util import custom
import re


MINIEDIT_VERSION = '2.2.0.1'
MININET_VERSION = re.sub(r'[^\d\.]', '', VERSION)

TOPODEF = 'none'
TOPOS = {'minimal': lambda: SingleSwitchTopo(k=2),
         'linear': LinearTopo,
         'reversed': SingleSwitchReversedTopo,
         'single': SingleSwitchTopo,
         'none': None,
         'tree': TreeTopo}
CONTROLLERDEF = 'ref'
CONTROLLERS = {'ref': Controller,
               'ovsc': OVSController,
               'nox': NOX,
               'remote': RemoteController,
               'none': lambda name: None}
LINKDEF = 'default'
LINKS = {'default': Link,
         'tc': TCLink}
HOSTDEF = 'proc'
HOSTS = {'proc': Host,
         'rt': custom(CPULimitedHost, sched='rt'),
         'cfs': custom(CPULimitedHost, sched='cfs')}