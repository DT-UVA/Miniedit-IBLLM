from mininet.log import warn
from mininet.util import netParse, ipAdd, StrictVersion
from tkinter import filedialog as tkFileDialog
import json

from modules.miniedit_utils.definitions import MININET_VERSION

def saveTopology(self):
    "Save command."
    myFormats = [
        ('Mininet Topology', '*.mn'),
        ('All Files', '*'),
    ]

    savingDictionary = {}
    fileName = tkFileDialog.asksaveasfilename(
        filetypes=myFormats, title="Save the topology as...")
    if len(fileName) > 0:
        # Save Application preferences
        savingDictionary['version'] = '2'

        # Save Switches and Hosts
        hostsToSave = []
        switchesToSave = []
        controllersToSave = []
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)
            x1, y1 = self.canvas.coords(item)
            if 'Switch' in tags or 'LegacySwitch' in tags or 'LegacyRouter' in tags:
                nodeNum = self.switchOpts[name]['nodeNum']
                nodeToSave = {'number': str(nodeNum),
                              'x': str(x1),
                              'y': str(y1),
                              'opts': self.switchOpts[name]}
                switchesToSave.append(nodeToSave)
            elif 'Host' in tags:
                nodeNum = self.hostOpts[name]['nodeNum']
                nodeToSave = {'number': str(nodeNum),
                              'x': str(x1),
                              'y': str(y1),
                              'opts': self.hostOpts[name]}
                hostsToSave.append(nodeToSave)
            elif 'Controller' in tags:
                nodeToSave = {'x': str(x1),
                              'y': str(y1),
                              'opts': self.controllers[name]}
                controllersToSave.append(nodeToSave)
            else:
                raise Exception("Cannot create mystery node: " + name)
        savingDictionary['hosts'] = hostsToSave
        savingDictionary['switches'] = switchesToSave
        savingDictionary['controllers'] = controllersToSave

        # Save Links
        linksToSave = []
        for link in self.links.values():
            src = link['src']
            dst = link['dest']
            linkopts = link['linkOpts']

            srcName, dstName = src['text'], dst['text']
            linkToSave = {'src': srcName,
                          'dest': dstName,
                          'opts': linkopts}
            if link['type'] == 'data':
                linksToSave.append(linkToSave)
        savingDictionary['links'] = linksToSave

        # Save Application preferences
        savingDictionary['application'] = self.appPrefs

        try:
            with open(fileName, 'w') as f:
                f.write(
                    json.dumps(savingDictionary,
                               sort_keys=True,
                               indent=4, separators=(',', ': ')))
        except Exception as er:  # pylint: disable=broad-except
            warn(er, '\n')


def exportScript(self):
    "Export command."
    myFormats = [
        ('Mininet Custom Topology', '*.py'),
        ('All Files', '*'),
    ]

    fileName = tkFileDialog.asksaveasfilename(
        filetypes=myFormats, title="Export the topology as...")
    if len(fileName) > 0:
        # debug( "Now saving under %s\n" % fileName )
        f = open(fileName, 'w')  # pylint: disable=consider-using-with

        f.write("#!/usr/bin/env python\n")
        f.write("\n")
        f.write("from mininet.net import Mininet\n")
        f.write(
            "from mininet.node import Controller, RemoteController, OVSController\n")
        f.write("from mininet.node import CPULimitedHost, Host, Node\n")
        f.write("from mininet.node import OVSKernelSwitch, UserSwitch\n")
        if StrictVersion(MININET_VERSION) > StrictVersion('2.0'):
            f.write("from mininet.node import IVSSwitch\n")
        f.write("from mininet.cli import CLI\n")
        f.write("from mininet.log import setLogLevel, info\n")
        f.write("from mininet.link import TCLink, Intf\n")
        f.write("from subprocess import call\n")

        inBandCtrl = False
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)

            if 'Controller' in tags:
                opts = self.controllers[name]
                controllerType = opts['controllerType']
                if controllerType == 'inband':
                    inBandCtrl = True

        if inBandCtrl:
            f.write("\n")
            f.write("class InbandController( RemoteController ):\n")
            f.write("\n")
            f.write("    def checkListening( self ):\n")
            f.write("        \"Overridden to do nothing.\"\n")
            f.write("        return\n")

        f.write("\n")
        f.write("def myNetwork():\n")
        f.write("\n")
        f.write("    net = Mininet( topo=None,\n")
        if len(self.appPrefs['dpctl']) > 0:
            f.write("                   listenPort=" +
                    self.appPrefs['dpctl']+",\n")
        f.write("                   build=False,\n")
        f.write("                   ipBase='" +
                self.appPrefs['ipBase']+"')\n")
        f.write("\n")
        f.write("    info( '*** Adding controller\\n' )\n")
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)

            if 'Controller' in tags:
                opts = self.controllers[name]
                controllerType = opts['controllerType']
                if 'controllerProtocol' in opts:
                    controllerProtocol = opts['controllerProtocol']
                else:
                    controllerProtocol = 'tcp'
                controllerIP = opts['remoteIP']
                controllerPort = opts['remotePort']

                f.write("    "+name +
                        "=net.addController(name='"+name+"',\n")

                if controllerType == 'remote':
                    f.write(
                        "                      controller=RemoteController,\n")
                    f.write("                      ip='" +
                            controllerIP+"',\n")
                elif controllerType == 'inband':
                    f.write(
                        "                      controller=InbandController,\n")
                    f.write("                      ip='" +
                            controllerIP+"',\n")
                elif controllerType == 'ovsc':
                    f.write(
                        "                      controller=OVSController,\n")
                else:
                    f.write("                      controller=Controller,\n")

                f.write("                      protocol='" +
                        controllerProtocol+"',\n")
                f.write("                      port=" +
                        str(controllerPort)+")\n")
                f.write("\n")

        # Save Switches and Hosts
        f.write("    info( '*** Add switches\\n')\n")
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)
            if 'LegacyRouter' in tags:
                f.write("    "+name+" = net.addHost('" +
                        name+"', cls=Node, ip='0.0.0.0')\n")
                f.write("    "+name +
                        ".cmd('sysctl -w net.ipv4.ip_forward=1')\n")
            if 'LegacySwitch' in tags:
                f.write("    "+name+" = net.addSwitch('"+name +
                        "', cls=OVSKernelSwitch, failMode='standalone')\n")
            if 'Switch' in tags:
                opts = self.switchOpts[name]
                nodeNum = opts['nodeNum']
                f.write("    "+name+" = net.addSwitch('"+name+"'")
                if opts['switchType'] == 'default':
                    if self.appPrefs['switchType'] == 'ivs':
                        f.write(", cls=IVSSwitch")
                    elif self.appPrefs['switchType'] == 'user':
                        f.write(", cls=UserSwitch")
                    elif self.appPrefs['switchType'] == 'userns':
                        f.write(", cls=UserSwitch, inNamespace=True")
                    else:
                        f.write(", cls=OVSKernelSwitch")
                elif opts['switchType'] == 'ivs':
                    f.write(", cls=IVSSwitch")
                elif opts['switchType'] == 'user':
                    f.write(", cls=UserSwitch")
                elif opts['switchType'] == 'userns':
                    f.write(", cls=UserSwitch, inNamespace=True")
                else:
                    f.write(", cls=OVSKernelSwitch")
                if 'dpctl' in opts:
                    f.write(", listenPort="+opts['dpctl'])
                if 'dpid' in opts:
                    f.write(", dpid='"+opts['dpid']+"'")
                f.write(")\n")
                if 'externalInterfaces' in opts:
                    for extInterface in opts['externalInterfaces']:
                        f.write(
                            "    Intf( '"+extInterface+"', node="+name+" )\n")

        f.write("\n")
        f.write("    info( '*** Add hosts\\n')\n")
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)
            if 'Host' in tags:
                opts = self.hostOpts[name]
                ip = None
                defaultRoute = None
                if 'defaultRoute' in opts and len(opts['defaultRoute']) > 0:
                    defaultRoute = "'via "+opts['defaultRoute']+"'"
                else:
                    defaultRoute = 'None'
                if 'ip' in opts and len(opts['ip']) > 0:
                    ip = opts['ip']
                else:
                    nodeNum = self.hostOpts[name]['nodeNum']
                    ipBaseNum, prefixLen = netParse(
                        self.appPrefs['ipBase'])
                    ip = ipAdd(i=nodeNum, prefixLen=prefixLen,
                               ipBaseNum=ipBaseNum)

                if 'cores' in opts or 'cpu' in opts:
                    f.write("    "+name+" = net.addHost('"+name +
                            "', cls=CPULimitedHost, ip='"+ip+"', defaultRoute="+defaultRoute+")\n")
                    if 'cores' in opts:
                        f.write("    "+name +
                                ".setCPUs(cores='"+opts['cores']+"')\n")
                    if 'cpu' in opts:
                        f.write(
                            "    "+name+".setCPUFrac(f="+str(opts['cpu'])+", sched='"+opts['sched']+"')\n")
                else:
                    f.write("    "+name+" = net.addHost('"+name +
                            "', cls=Host, ip='"+ip+"', defaultRoute="+defaultRoute+")\n")
                if 'externalInterfaces' in opts:
                    for extInterface in opts['externalInterfaces']:
                        f.write(
                            "    Intf( '"+extInterface+"', node="+name+" )\n")
        f.write("\n")

        # Save Links
        f.write("    info( '*** Add links\\n')\n")
        for key, linkDetail in self.links.items():
            tags = self.canvas.gettags(key)
            if 'data' in tags:
                optsExist = False
                src = linkDetail['src']
                dst = linkDetail['dest']
                linkopts = linkDetail['linkOpts']
                srcName, dstName = src['text'], dst['text']
                bw = ''
                # delay = ''
                # loss = ''
                # max_queue_size = ''
                linkOpts = "{"
                if 'bw' in linkopts:
                    bw = linkopts['bw']
                    linkOpts = linkOpts + "'bw':"+str(bw)
                    optsExist = True
                if 'delay' in linkopts:
                    # delay =  linkopts['delay']
                    if optsExist:
                        linkOpts = linkOpts + ","
                    linkOpts = linkOpts + "'delay':'"+linkopts['delay']+"'"
                    optsExist = True
                if 'loss' in linkopts:
                    if optsExist:
                        linkOpts = linkOpts + ","
                    linkOpts = linkOpts + "'loss':"+str(linkopts['loss'])
                    optsExist = True
                if 'max_queue_size' in linkopts:
                    if optsExist:
                        linkOpts = linkOpts + ","
                    linkOpts = linkOpts + "'max_queue_size':" + \
                        str(linkopts['max_queue_size'])
                    optsExist = True
                if 'jitter' in linkopts:
                    if optsExist:
                        linkOpts = linkOpts + ","
                    linkOpts = linkOpts + "'jitter':'" + \
                        linkopts['jitter']+"'"
                    optsExist = True
                if 'speedup' in linkopts:
                    if optsExist:
                        linkOpts = linkOpts + ","
                    linkOpts = linkOpts + "'speedup':" + \
                        str(linkopts['speedup'])
                    optsExist = True

                linkOpts = linkOpts + "}"
                if optsExist:
                    f.write("    "+srcName+dstName+" = "+linkOpts+"\n")
                f.write("    net.addLink("+srcName+", "+dstName)
                if optsExist:
                    f.write(", cls=TCLink , **"+srcName+dstName)
                f.write(")\n")

        f.write("\n")
        f.write("    info( '*** Starting network\\n')\n")
        f.write("    net.build()\n")

        f.write("    info( '*** Starting controllers\\n')\n")
        f.write("    for controller in net.controllers:\n")
        f.write("        controller.start()\n")
        f.write("\n")

        f.write("    info( '*** Starting switches\\n')\n")
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)
            if 'Switch' in tags or 'LegacySwitch' in tags:
                opts = self.switchOpts[name]
                ctrlList = ",".join(opts['controllers'])
                f.write("    net.get('"+name+"').start(["+ctrlList+"])\n")

        f.write("\n")

        f.write("    info( '*** Post configure switches and hosts\\n')\n")
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)
            if 'Switch' in tags:
                opts = self.switchOpts[name]
                if opts['switchType'] == 'default':
                    if self.appPrefs['switchType'] == 'user':
                        if 'switchIP' in opts:
                            if len(opts['switchIP']) > 0:
                                f.write(
                                    "    "+name+".cmd('ifconfig "+name+" "+opts['switchIP']+"')\n")
                    elif self.appPrefs['switchType'] == 'userns':
                        if 'switchIP' in opts:
                            if len(opts['switchIP']) > 0:
                                f.write(
                                    "    "+name+".cmd('ifconfig lo "+opts['switchIP']+"')\n")
                    elif self.appPrefs['switchType'] == 'ovs':
                        if 'switchIP' in opts:
                            if len(opts['switchIP']) > 0:
                                f.write(
                                    "    "+name+".cmd('ifconfig "+name+" "+opts['switchIP']+"')\n")
                elif opts['switchType'] == 'user':
                    if 'switchIP' in opts:
                        if len(opts['switchIP']) > 0:
                            f.write("    "+name+".cmd('ifconfig " +
                                    name+" "+opts['switchIP']+"')\n")
                elif opts['switchType'] == 'userns':
                    if 'switchIP' in opts:
                        if len(opts['switchIP']) > 0:
                            f.write(
                                "    "+name+".cmd('ifconfig lo "+opts['switchIP']+"')\n")
                elif opts['switchType'] == 'ovs':
                    if 'switchIP' in opts:
                        if len(opts['switchIP']) > 0:
                            f.write("    "+name+".cmd('ifconfig " +
                                    name+" "+opts['switchIP']+"')\n")
        for widget, item in self.widgetToItem.items():
            name = widget['text']
            tags = self.canvas.gettags(item)
            if 'Host' in tags:
                opts = self.hostOpts[name]
                # Attach vlan interfaces
                if 'vlanInterfaces' in opts:
                    for vlanInterface in opts['vlanInterfaces']:
                        f.write("    "+name+".cmd('vconfig add " +
                                name+"-eth0 "+vlanInterface[1]+"')\n")
                        f.write("    "+name+".cmd('ifconfig "+name+"-eth0." +
                                vlanInterface[1]+" "+vlanInterface[0]+"')\n")
                # Run User Defined Start Command
                if 'startCommand' in opts:
                    f.write("    "+name+".cmdPrint('" +
                            opts['startCommand']+"')\n")
            if 'Switch' in tags:
                opts = self.switchOpts[name]
                # Run User Defined Start Command
                if 'startCommand' in opts:
                    f.write("    "+name+".cmdPrint('" +
                            opts['startCommand']+"')\n")

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
                f.write("    \n")
                f.write("    call('"+nflowCmd+nflowSwitches+"', shell=True)\n")

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
                            sflowSwitches = sflowSwitches+' -- set Bridge '+name+' sflow=@MiniEditSF'
                            sflowEnabled = True
            if sflowEnabled:
                sflowCmd = 'ovs-vsctl -- --id=@MiniEditSF create sFlow ' + 'target=\\\"' + \
                    sflowValues['sflowTarget']+'\\\" ' + 'header='+sflowValues['sflowHeader']+' ' + \
                    'sampling='+sflowValues['sflowSampling'] + \
                    ' ' + 'polling='+sflowValues['sflowPolling']
                f.write("    \n")
                f.write("    call('"+sflowCmd+sflowSwitches+"', shell=True)\n")

        f.write("\n")
        f.write("    CLI(net)\n")
        for widget, item in self.widgetToItem:
            name = widget['text']
            tags = self.canvas.gettags(item)
            if 'Host' in tags:
                opts = self.hostOpts[name]
                # Run User Defined Stop Command
                if 'stopCommand' in opts:
                    f.write("    "+name+".cmdPrint('" +
                            opts['stopCommand']+"')\n")
            if 'Switch' in tags:
                opts = self.switchOpts[name]
                # Run User Defined Stop Command
                if 'stopCommand' in opts:
                    f.write("    "+name+".cmdPrint('" +
                            opts['stopCommand']+"')\n")

        f.write("    net.stop()\n")
        f.write("\n")
        f.write("if __name__ == '__main__':\n")
        f.write("    setLogLevel( 'info' )\n")
        f.write("    myNetwork()\n")
        f.write("\n")

        f.close()
