from subprocess import call

from mininet.util import StrictVersion
from mininet.term import makeTerm

# Import all the definitions
from modules.miniedit_utils.definitions import MININET_VERSION

def xterm(self, _ignore=None):
    "Make an xterm when a button is pressed."
    if (self.selection is None or
        self.net is None or
            self.selection not in self.itemToWidget):
        return
    name = self.itemToWidget[self.selection]['text']
    if name not in self.net.nameToNode:
        return
    term = makeTerm(
        self.net.nameToNode[name], 'Host', term=self.appPrefs['terminalType'])
    if StrictVersion(MININET_VERSION) > StrictVersion('2.0'):
        self.net.terms += term
    else:
        self.net.terms.append(term)

def iperf(self, _ignore=None):
    "Make an xterm when a button is pressed."
    if (self.selection is None or
        self.net is None or
            self.selection not in self.itemToWidget):
        return
    name = self.itemToWidget[self.selection]['text']
    if name not in self.net.nameToNode:
        return
    self.net.nameToNode[name].cmd('iperf -s -p 5001 &')

@staticmethod
def ovsShow(_ignore=None):
    call(["xterm -T 'OVS Summary' -sb -sl 2000 -e 'ovs-vsctl show; read -p \"Press Enter to close\"' &"], shell=True)

@staticmethod
def rootTerminal(_ignore=None):
    call(["xterm -T 'Root Terminal' -sb -sl 2000 &"], shell=True)