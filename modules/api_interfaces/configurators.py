import re

from functools import partial
from subprocess import call

from mininet.net import Mininet
from mininet.log import info, debug
from mininet.util import netParse, ipAdd, quietRun
from mininet.node import Controller, RemoteController, OVSController, CPULimitedHost, Host, IVSSwitch
from mininet.link import TCLink, Intf
from mininet.moduledeps import moduleDeps
from mininet.cli import CLI


# Import Tkinter
from tkinter.messagebox import showerror

# Import all the dialogs
from modules.dialogs.host_dialog import HostDialog
from modules.dialogs.switch_dialog import SwitchDialog
from modules.dialogs.preferences import PrefsDialog
from modules.dialogs.link_dialog import LinkDialog
from modules.dialogs.controller_dialog import ControllerDialog

# Custom devices
from modules.devices.inband_controller import InbandController
from modules.devices.custom_user_switch import CustomUserSwitch
from modules.devices.legacy_router import LegacyRouter
from modules.devices.legacy_switch import LegacySwitch
from modules.devices.custom_ovs import customOvs

# Import all the definitions
from modules.miniedit_utils.definitions import *


@staticmethod
def checkIntf(intf):
    "Make sure intf exists and is not configured."
    if (' %s:' % intf) not in quietRun('ip link show'):
        showerror(title="Error",
                  message='External interface ' + intf + ' does not exist! Skipping.')
        return False
    ips = re.findall(r'\d+\.\d+\.\d+\.\d+', quietRun('ifconfig ' + intf))
    if ips:
        showerror(title="Error",
                  message=intf + ' has an IP address and is probably in use! Skipping.')
        return False
    return True


def hostDetails(self, _ignore=None):
    if (self.selection is None or
        self.net is not None or
            self.selection not in self.itemToWidget):
        return
    widget = self.itemToWidget[self.selection]
    name = widget['text']
    tags = self.canvas.gettags(self.selection)
    if 'Host' not in tags:
        return

    prefDefaults = self.hostOpts[name]
    hostBox = HostDialog(self, title='Host Details',
                         prefDefaults=prefDefaults)
    self.master.wait_window(hostBox.top)
    if hostBox.result:
        newHostOpts = {'nodeNum': self.hostOpts[name]['nodeNum']}
        newHostOpts['sched'] = hostBox.result['sched']
        if len(hostBox.result['startCommand']) > 0:
            newHostOpts['startCommand'] = hostBox.result['startCommand']
        if len(hostBox.result['stopCommand']) > 0:
            newHostOpts['stopCommand'] = hostBox.result['stopCommand']
        if len(hostBox.result['cpu']) > 0:
            newHostOpts['cpu'] = float(hostBox.result['cpu'])
        if len(hostBox.result['cores']) > 0:
            newHostOpts['cores'] = hostBox.result['cores']
        if len(hostBox.result['hostname']) > 0:
            newHostOpts['hostname'] = hostBox.result['hostname']
            name = hostBox.result['hostname']
            widget['text'] = name
        if len(hostBox.result['defaultRoute']) > 0:
            newHostOpts['defaultRoute'] = hostBox.result['defaultRoute']
        if len(hostBox.result['ip']) > 0:
            newHostOpts['ip'] = hostBox.result['ip']
        if len(hostBox.result['externalInterfaces']) > 0:
            newHostOpts['externalInterfaces'] = hostBox.result['externalInterfaces']
        if len(hostBox.result['vlanInterfaces']) > 0:
            newHostOpts['vlanInterfaces'] = hostBox.result['vlanInterfaces']
        if len(hostBox.result['privateDirectory']) > 0:
            newHostOpts['privateDirectory'] = hostBox.result['privateDirectory']
        self.hostOpts[name] = newHostOpts
        info('New host details for ' + name +
             ' = ' + str(newHostOpts), '\n')


def switchDetails(self, _ignore=None):
    if (self.selection is None or
        self.net is not None or
            self.selection not in self.itemToWidget):
        return
    widget = self.itemToWidget[self.selection]
    name = widget['text']
    tags = self.canvas.gettags(self.selection)
    if 'Switch' not in tags:
        return

    prefDefaults = self.switchOpts[name]
    switchBox = SwitchDialog(
        self, title='Switch Details', prefDefaults=prefDefaults)
    self.master.wait_window(switchBox.top)
    if switchBox.result:
        newSwitchOpts = {'nodeNum': self.switchOpts[name]['nodeNum']}
        newSwitchOpts['switchType'] = switchBox.result['switchType']
        newSwitchOpts['controllers'] = self.switchOpts[name]['controllers']
        if len(switchBox.result['startCommand']) > 0:
            newSwitchOpts['startCommand'] = switchBox.result['startCommand']
        if len(switchBox.result['stopCommand']) > 0:
            newSwitchOpts['stopCommand'] = switchBox.result['stopCommand']
        if len(switchBox.result['dpctl']) > 0:
            newSwitchOpts['dpctl'] = switchBox.result['dpctl']
        if len(switchBox.result['dpid']) > 0:
            newSwitchOpts['dpid'] = switchBox.result['dpid']
        if len(switchBox.result['hostname']) > 0:
            newSwitchOpts['hostname'] = switchBox.result['hostname']
            name = switchBox.result['hostname']
            widget['text'] = name
        if len(switchBox.result['externalInterfaces']) > 0:
            newSwitchOpts['externalInterfaces'] = switchBox.result['externalInterfaces']
        newSwitchOpts['switchIP'] = switchBox.result['switchIP']
        newSwitchOpts['sflow'] = switchBox.result['sflow']
        newSwitchOpts['netflow'] = switchBox.result['netflow']
        self.switchOpts[name] = newSwitchOpts
        info('New switch details for ' + name +
             ' = ' + str(newSwitchOpts), '\n')


def linkUp(self):
    if (self.selection is None or
            self.net is None):
        return
    link = self.selection
    linkDetail = self.links[link]
    src = linkDetail['src']
    dst = linkDetail['dest']
    srcName, dstName = src['text'], dst['text']
    self.net.configLinkStatus(srcName, dstName, 'up')
    self.canvas.itemconfig(link, dash=())


def linkDown(self):
    if (self.selection is None or
            self.net is None):
        return
    link = self.selection
    linkDetail = self.links[link]
    src = linkDetail['src']
    dst = linkDetail['dest']
    srcName, dstName = src['text'], dst['text']
    self.net.configLinkStatus(srcName, dstName, 'down')
    self.canvas.itemconfig(link, dash=(4, 4))


def linkDetails(self, _ignore=None):
    if (self.selection is None or
            self.net is not None):
        return
    link = self.selection

    linkDetail = self.links[link]
    # src = linkDetail['src']
    # dest = linkDetail['dest']
    linkopts = linkDetail['linkOpts']
    linkBox = LinkDialog(self, title='Link Details', linkDefaults=linkopts)
    if linkBox.result is not None:
        linkDetail['linkOpts'] = linkBox.result
        info('New link details = ' + str(linkBox.result), '\n')


def prefDetails(self):
    prefDefaults = self.appPrefs
    prefBox = PrefsDialog(self, title='Preferences',
                          prefDefaults=prefDefaults)
    info('New Prefs = ' + str(prefBox.result), '\n')
    if prefBox.result:
        self.appPrefs = prefBox.result


def controllerDetails(self):
    if (self.selection is None or
        self.net is not None or
            self.selection not in self.itemToWidget):
        return
    widget = self.itemToWidget[self.selection]
    name = widget['text']
    tags = self.canvas.gettags(self.selection)
    oldName = name
    if 'Controller' not in tags:
        return

    ctrlrBox = ControllerDialog(
        self, title='Controller Details', ctrlrDefaults=self.controllers[name])
    if ctrlrBox.result:
        # debug( 'Controller is ' + ctrlrBox.result[0], '\n' )
        if len(ctrlrBox.result['hostname']) > 0:
            name = ctrlrBox.result['hostname']
            widget['text'] = name
        else:
            ctrlrBox.result['hostname'] = name
        self.controllers[name] = ctrlrBox.result
        info('New controller details for ' + name +
             ' = ' + str(self.controllers[name]), '\n')
        # Find references to controller and change name
        if oldName != name:
            for widget, item in self.widgetToItem.items():
                switchName = widget['text']
                tags = self.canvas.gettags(item)
                if 'Switch' in tags:
                    switch = self.switchOpts[switchName]
                    if oldName in switch['controllers']:
                        switch['controllers'].remove(oldName)
                        switch['controllers'].append(name)


def listBridge(self, _ignore=None):
    if (self.selection is None or
        self.net is None or
            self.selection not in self.itemToWidget):
        return
    name = self.itemToWidget[self.selection]['text']
    tags = self.canvas.gettags(self.selection)

    if name not in self.net.nameToNode:
        return
    if 'Switch' in tags or 'LegacySwitch' in tags:
        call(["xterm -T 'Bridge Details' -sb -sl 2000 -e 'ovs-vsctl list bridge " +
              name + "; read -p \"Press Enter to close\"' &"], shell=True)


def addLink(self, source, dest, linktype='data', linkopts=None):
    "Add link to model."
    if linkopts is None:
        linkopts = {}
    source.links[dest] = self.link
    dest.links[source] = self.link
    self.links[self.link] = {'type': linktype,
                             'src': source,
                             'dest': dest,
                             'linkOpts': linkopts}


def deleteLink(self, link):
    "Delete link from model."
    pair = self.links.get(link, None)
    if pair is not None:
        source = pair['src']
        dest = pair['dest']
        del source.links[dest]
        del dest.links[source]
        stags = self.canvas.gettags(self.widgetToItem[source])
        ltags = self.canvas.gettags(link)

        if 'control' in ltags:
            controllerName = ''
            switchName = ''
            if 'Controller' in stags:
                controllerName = source['text']
                switchName = dest['text']
            else:
                controllerName = dest['text']
                switchName = source['text']

            if controllerName in self.switchOpts[switchName]['controllers']:
                self.switchOpts[switchName]['controllers'].remove(
                    controllerName)

    if link is not None:
        del self.links[link]


def deleteNode(self, item):
    "Delete node (and its links) from model."
    widget = self.itemToWidget[item]
    tags = self.canvas.gettags(item)
    if 'Controller' in tags:
        # remove from switch controller lists
        for searchwidget, searchitem in self.widgetToItem.items():
            name = searchwidget['text']
            tags = self.canvas.gettags(searchitem)
            if 'Switch' in tags:
                if widget['text'] in self.switchOpts[name]['controllers']:
                    self.switchOpts[name]['controllers'].remove(
                        widget['text'])
    for link in tuple(widget.links.values()):
        # Delete from view and model
        self.deleteItem(link)
    del self.itemToWidget[item]
    del self.widgetToItem[widget]


def buildNodes(self, net):
    # Make nodes
    info("Getting Hosts and Switches.\n")
    for widget, item in self.widgetToItem.items():
        name = widget['text']
        tags = self.canvas.gettags(item)
        # debug( name+' has '+str(tags), '\n' )

        if 'Switch' in tags:
            opts = self.switchOpts[name]
            # debug( str(opts), '\n' )

            # Create the correct switch class
            switchClass = customOvs
            switchParms = {}
            if 'dpctl' in opts:
                switchParms['listenPort'] = int(opts['dpctl'])
            if 'dpid' in opts:
                switchParms['dpid'] = opts['dpid']
            if opts['switchType'] == 'default':
                if self.appPrefs['switchType'] == 'ivs':
                    switchClass = IVSSwitch
                elif self.appPrefs['switchType'] == 'user':
                    switchClass = CustomUserSwitch
                elif self.appPrefs['switchType'] == 'userns':
                    switchParms['inNamespace'] = True
                    switchClass = CustomUserSwitch
                else:
                    switchClass = customOvs
            elif opts['switchType'] == 'user':
                switchClass = CustomUserSwitch
            elif opts['switchType'] == 'userns':
                switchClass = CustomUserSwitch
                switchParms['inNamespace'] = True
            elif opts['switchType'] == 'ivs':
                switchClass = IVSSwitch
            else:
                switchClass = customOvs

            if switchClass == customOvs:
                # Set OpenFlow versions
                self.openFlowVersions = []
                if self.appPrefs['openFlowVersions']['ovsOf10'] == '1':
                    self.openFlowVersions.append('OpenFlow10')
                if self.appPrefs['openFlowVersions']['ovsOf11'] == '1':
                    self.openFlowVersions.append('OpenFlow11')
                if self.appPrefs['openFlowVersions']['ovsOf12'] == '1':
                    self.openFlowVersions.append('OpenFlow12')
                if self.appPrefs['openFlowVersions']['ovsOf13'] == '1':
                    self.openFlowVersions.append('OpenFlow13')
                protoList = ",".join(self.openFlowVersions)
                switchParms['protocols'] = protoList
            newSwitch = net.addSwitch(name, cls=switchClass, **switchParms)

            # Some post startup config
            if switchClass == CustomUserSwitch:
                if 'switchIP' in opts:
                    if len(opts['switchIP']) > 0:
                        newSwitch.setSwitchIP(opts['switchIP'])
            if switchClass == customOvs:
                if 'switchIP' in opts:
                    if len(opts['switchIP']) > 0:
                        newSwitch.setSwitchIP(opts['switchIP'])

            # Attach external interfaces
            if 'externalInterfaces' in opts:
                for extInterface in opts['externalInterfaces']:
                    if self.checkIntf(extInterface):
                        Intf(extInterface, node=newSwitch)

        elif 'LegacySwitch' in tags:
            newSwitch = net.addSwitch(name, cls=LegacySwitch)
        elif 'LegacyRouter' in tags:
            newSwitch = net.addHost(name, cls=LegacyRouter)
        elif 'Host' in tags:
            opts = self.hostOpts[name]
            # debug( str(opts), '\n' )
            ip = None
            defaultRoute = None
            if 'defaultRoute' in opts and len(opts['defaultRoute']) > 0:
                defaultRoute = 'via '+opts['defaultRoute']
            if 'ip' in opts and len(opts['ip']) > 0:
                ip = opts['ip']
            else:
                nodeNum = self.hostOpts[name]['nodeNum']
                ipBaseNum, prefixLen = netParse(self.appPrefs['ipBase'])
                ip = ipAdd(i=nodeNum, prefixLen=prefixLen,
                           ipBaseNum=ipBaseNum)

            # Create the correct host class
            if 'cores' in opts or 'cpu' in opts:
                if 'privateDirectory' in opts:
                    hostCls = partial(CPULimitedHost,
                                      privateDirs=opts['privateDirectory'])
                else:
                    hostCls = CPULimitedHost
            else:
                if 'privateDirectory' in opts:
                    hostCls = partial(Host,
                                      privateDirs=opts['privateDirectory'])
                else:
                    hostCls = Host
            debug(hostCls, '\n')
            newHost = net.addHost(name,
                                  cls=hostCls,
                                  ip=ip,
                                  defaultRoute=defaultRoute
                                  )

            # Set the CPULimitedHost specific options
            if 'cores' in opts:
                newHost.setCPUs(cores=opts['cores'])
            if 'cpu' in opts:
                newHost.setCPUFrac(f=opts['cpu'], sched=opts['sched'])

            # Attach external interfaces
            if 'externalInterfaces' in opts:
                for extInterface in opts['externalInterfaces']:
                    if self.checkIntf(extInterface):
                        Intf(extInterface, node=newHost)
            if 'vlanInterfaces' in opts:
                if len(opts['vlanInterfaces']) > 0:
                    info('Checking that OS is VLAN prepared\n')
                    self.pathCheck('vconfig', moduleName='vlan package')
                    moduleDeps(add='8021q')
        elif 'Controller' in tags:
            opts = self.controllers[name]

            # Get controller info from panel
            controllerType = opts['controllerType']
            if 'controllerProtocol' in opts:
                controllerProtocol = opts['controllerProtocol']
            else:
                controllerProtocol = 'tcp'
                opts['controllerProtocol'] = 'tcp'
            controllerIP = opts['remoteIP']
            controllerPort = opts['remotePort']

            # Make controller
            info('Getting controller selection:'+controllerType, '\n')
            if controllerType == 'remote':
                net.addController(name=name,
                                  controller=RemoteController,
                                  ip=controllerIP,
                                  protocol=controllerProtocol,
                                  port=controllerPort)
            elif controllerType == 'inband':
                net.addController(name=name,
                                  controller=InbandController,
                                  ip=controllerIP,
                                  protocol=controllerProtocol,
                                  port=controllerPort)
            elif controllerType == 'ovsc':
                net.addController(name=name,
                                  controller=OVSController,
                                  protocol=controllerProtocol,
                                  port=controllerPort)
            else:
                net.addController(name=name,
                                  controller=Controller,
                                  protocol=controllerProtocol,
                                  port=controllerPort)

        else:
            raise Exception("Cannot create mystery node: " + name)


def buildLinks(self, net):
    # Make links
    info("Getting Links.\n")
    for key, link in self.links.items():
        tags = self.canvas.gettags(key)
        if 'data' in tags:
            src = link['src']
            dst = link['dest']
            linkopts = link['linkOpts']
            srcName, dstName = src['text'], dst['text']
            srcNode, dstNode = net.nameToNode[srcName], net.nameToNode[dstName]
            if linkopts:
                net.addLink(srcNode, dstNode, cls=TCLink, **linkopts)
            else:
                # debug( str(srcNode) )
                # debug( str(dstNode), '\n' )
                net.addLink(srcNode, dstNode)
            self.canvas.itemconfig(key, dash=())


@staticmethod
def pathCheck(*args, **kwargs):
    "Make sure each program in *args can be found in $PATH."
    moduleName = kwargs.get('moduleName', 'it')
    for arg in args:
        if not quietRun('which ' + arg):
            showerror(title="Error",
                      message='Cannot find required executable %s.\n' % arg +
                      'Please make sure that %s is installed ' % moduleName +
                      'and available in your $PATH.')


def build(self):
    "Build network based on our topology."

    dpctl = None
    if len(self.appPrefs['dpctl']) > 0:
        dpctl = int(self.appPrefs['dpctl'])
    net = Mininet(topo=None,
                  listenPort=dpctl,
                  build=False,
                  ipBase=self.appPrefs['ipBase'])

    self.buildNodes(net)
    self.buildLinks(net)

    # Build network (we have to do this separately at the moment )
    net.build()

    return net


def postStartSetup(self):
    # Setup host details
    for widget, item in self.widgetToItem.items():
        name = widget['text']
        tags = self.canvas.gettags(item)
        if 'Host' in tags:
            newHost = self.net.get(name)
            opts = self.hostOpts[name]
            # Attach vlan interfaces
            if 'vlanInterfaces' in opts:
                for vlanInterface in opts['vlanInterfaces']:
                    info('adding vlan interface '+vlanInterface[1], '\n')
                    newHost.cmdPrint(
                        'ifconfig '+name+'-eth0.'+vlanInterface[1]+' '+vlanInterface[0])
            # Run User Defined Start Command
            if 'startCommand' in opts:
                newHost.cmdPrint(opts['startCommand'])
        if 'Switch' in tags:
            newNode = self.net.get(name)
            opts = self.switchOpts[name]
            # Run User Defined Start Command
            if 'startCommand' in opts:
                newNode.cmdPrint(opts['startCommand'])

    # Configure NetFlow
    nflowValues = self.appPrefs['netflow']
    if len(nflowValues['nflowTarget']) > 0:
        nflowEnabled = False
        nflowSwitches = ''
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)

            if 'Switch' in tags:
                opts = self.switchOpts[name]
                if 'netflow' in opts:
                    if opts['netflow'] == '1':
                        info(name+' has Netflow enabled\n')
                        nflowSwitches = nflowSwitches+' -- set Bridge '+name+' netflow=@MiniEditNF'
                        nflowEnabled = True
        if nflowEnabled:
            nflowCmd = 'ovs-vsctl -- --id=@MiniEditNF create NetFlow ' + 'target=\\\"' + \
                nflowValues['nflowTarget']+'\\\" ' + \
                'active-timeout='+nflowValues['nflowTimeout']
            if nflowValues['nflowAddId'] == '1':
                nflowCmd = nflowCmd + ' add_id_to_interface=true'
            else:
                nflowCmd = nflowCmd + ' add_id_to_interface=false'
            info('cmd = '+nflowCmd+nflowSwitches, '\n')
            call(nflowCmd+nflowSwitches, shell=True)

        else:
            info('No switches with Netflow\n')
    else:
        info('No NetFlow targets specified.\n')

    # Configure sFlow
    sflowValues = self.appPrefs['sflow']
    if len(sflowValues['sflowTarget']) > 0:
        sflowEnabled = False
        sflowSwitches = ''
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)

            if 'Switch' in tags:
                opts = self.switchOpts[name]
                if 'sflow' in opts:
                    if opts['sflow'] == '1':
                        info(name+' has sflow enabled\n')
                        sflowSwitches = sflowSwitches+' -- set Bridge '+name+' sflow=@MiniEditSF'
                        sflowEnabled = True
        if sflowEnabled:
            sflowCmd = 'ovs-vsctl -- --id=@MiniEditSF create sFlow ' + 'target=\\\"' + \
                sflowValues['sflowTarget']+'\\\" ' + 'header='+sflowValues['sflowHeader']+' ' + \
                'sampling='+sflowValues['sflowSampling'] + \
                ' ' + 'polling='+sflowValues['sflowPolling']
            info('cmd = '+sflowCmd+sflowSwitches, '\n')
            call(sflowCmd+sflowSwitches, shell=True)

        else:
            info('No switches with sflow\n')
    else:
        info('No sFlow targets specified.\n')

    # NOTE: MAKE SURE THIS IS LAST THING CALLED
    # Start the CLI if enabled
    if self.appPrefs['startCLI'] == '1':
        info("\n\n NOTE: PLEASE REMEMBER TO EXIT THE CLI BEFORE YOU PRESS THE STOP BUTTON. Not exiting will prevent MiniEdit from quitting and will prevent you from starting the network again during this session.\n\n")
        CLI(self.net)
