from optparse import OptionParser
from mininet.util import customClass, buildTopo
from sys import exit, argv
from mininet.log import info
from mininet.net import Mininet

from modules.miniedit_utils.definitions import TOPOS, TOPODEF, LINKS, LINKDEF


def parseArgs(self):
    """Parse command-line args and return options object.
       returns: opts parse options dict"""

    if '--custom' in argv:
        index = argv.index('--custom')
        if len(argv) > index + 1:
            filename = argv[index + 1]
            self.parseCustomFile(filename)
        else:
            raise Exception('Custom file name not found')

    desc = ("The %prog utility creates Mininet network from the\n"
            "command line. It can create parametrized topologies,\n"
            "invoke the Mininet CLI, and run tests.")

    usage = ('%prog [options]\n'
             '(type %prog -h for details)')

    opts = OptionParser(description=desc, usage=usage)

    addDictOption(opts, TOPOS, TOPODEF, 'topo')
    addDictOption(opts, LINKS, LINKDEF, 'link')

    opts.add_option('--custom', type='string', default=None,
                    help='read custom topo and node params from .py ' +
                    'file')

    self.options, self.args = opts.parse_args()
    # We don't accept extra arguments after the options
    if self.args:
        opts.print_help()
        exit()


def setCustom(self, name, value):
    "Set custom parameters for MininetRunner."
    if name in ('topos', 'switches', 'hosts', 'controllers'):
        # Update dictionaries
        param = name.upper()
        globals()[param].update(value)
    elif name == 'validate':
        # Add custom validate function
        self.validate = value
    else:
        # Add or modify global variable or class
        globals()[name] = value


def parseCustomFile(self, fileName):
    "Parse custom file and add params before parsing cmd-line options."
    customs = {}
    if os.path.isfile(fileName):
        with open(fileName, 'r') as f:
            exec(f.read())  # pylint: disable=exec-used
        for name, val in customs.items():
            self.setCustom(name, val)
    else:
        raise Exception('could not find custom file: %s' % fileName)


def importTopo(self):
    info('topo='+self.options.topo, '\n')
    if self.options.topo == 'none':
        return
    self.newTopology()
    topo = buildTopo(TOPOS, self.options.topo)
    link = customClass(LINKS, self.options.link)
    importNet = Mininet(topo=topo, build=False, link=link)
    importNet.build()

    c = self.canvas
    rowIncrement = 100
    currentY = 100

    # Add Controllers
    info('controllers:'+str(len(importNet.controllers)), '\n')
    for controller in importNet.controllers:
        name = controller.name
        x = self.controllerCount*100+100
        self.addNode('Controller', self.controllerCount,
                     float(x), float(currentY), name=name)
        icon = self.findWidgetByName(name)
        icon.bind('<Button-3>', self.do_controllerPopup)
        ctrlr = {'controllerType': 'ref',
                 'hostname': name,
                 'controllerProtocol': controller.protocol,
                 'remoteIP': controller.ip,
                 'remotePort': controller.port}
        self.controllers[name] = ctrlr

    currentY = currentY + rowIncrement

    # Add switches
    info('switches:'+str(len(importNet.switches)), '\n')
    columnCount = 0
    for switch in importNet.switches:
        name = switch.name
        self.switchOpts[name] = {}
        self.switchOpts[name]['nodeNum'] = self.switchCount
        self.switchOpts[name]['hostname'] = name
        self.switchOpts[name]['switchType'] = 'default'
        self.switchOpts[name]['controllers'] = []

        x = columnCount*100+100
        self.addNode('Switch', self.switchCount,
                     float(x), float(currentY), name=name)
        icon = self.findWidgetByName(name)
        icon.bind('<Button-3>', self.do_switchPopup)
        # Now link to controllers
        for controller in importNet.controllers:
            self.switchOpts[name]['controllers'].append(controller.name)
            dest = self.findWidgetByName(controller.name)
            dx, dy = c.coords(self.widgetToItem[dest])
            self.link = c.create_line(float(x),
                                      float(currentY),
                                      dx,
                                      dy,
                                      width=4,
                                      fill='red',
                                      dash=(6, 4, 2, 4),
                                      tag='link')
            c.itemconfig(self.link, tags=c.gettags(self.link)+('control',))
            self.addLink(icon, dest, linktype='control')
            self.createControlLinkBindings()
            self.link = self.linkWidget = None
        if columnCount == 9:
            columnCount = 0
            currentY = currentY + rowIncrement
        else:
            columnCount = columnCount+1

    currentY = currentY + rowIncrement
    # Add hosts
    info('hosts:'+str(len(importNet.hosts)), '\n')
    columnCount = 0
    for host in importNet.hosts:
        name = host.name
        self.hostOpts[name] = {'sched': 'host'}
        self.hostOpts[name]['nodeNum'] = self.hostCount
        self.hostOpts[name]['hostname'] = name
        self.hostOpts[name]['ip'] = host.IP()

        x = columnCount*100+100
        self.addNode('Host', self.hostCount,
                     float(x), float(currentY), name=name)
        icon = self.findWidgetByName(name)
        icon.bind('<Button-3>', self.do_hostPopup)
        if columnCount == 9:
            columnCount = 0
            currentY = currentY + rowIncrement
        else:
            columnCount = columnCount+1

    info('links:'+str(len(topo.links())), '\n')
    # [('h1', 's3'), ('h2', 's4'), ('s3', 's4')]
    for link in topo.links():
        info(str(link), '\n')
        srcNode = link[0]
        src = self.findWidgetByName(srcNode)
        sx, sy = self.canvas.coords(self.widgetToItem[src])

        destNode = link[1]
        dest = self.findWidgetByName(destNode)
        dx, dy = self.canvas.coords(self.widgetToItem[dest])

        params = topo.linkInfo(srcNode, destNode)
        info('Link Parameters='+str(params), '\n')

        self.link = self.canvas.create_line(sx, sy, dx, dy, width=4,
                                            fill='blue', tag='link')
        c.itemconfig(self.link, tags=c.gettags(self.link)+('data',))
        self.addLink(src, dest, linkopts=params)
        self.createDataLinkBindings()
        self.link = self.linkWidget = None

    importNet.stop()


def addDictOption(opts, choicesDict, default, name, helpStr=None):
    """Convenience function to add choices dicts to OptionParser.
       opts: OptionParser instance
       choicesDict: dictionary of valid choices, must include default
       default: default choice key
       name: long option name
       help: string"""
    if default not in choicesDict:
        raise Exception('Invalid  default %s for choices dict: %s' %
                        (default, name))
    if not helpStr:
        helpStr = ('|'.join(sorted(choicesDict.keys())) +
                   '[,param=value...]')
    opts.add_option('--' + name,
                    type='string',
                    default=default,
                    help=helpStr)
