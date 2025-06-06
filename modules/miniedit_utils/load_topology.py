from tkinter import filedialog as tkFileDialog
import json

def loadTopology(self):
        "Load command."
        c = self.canvas

        myFormats = [
            ('Mininet Topology', '*.mn'),
            ('All Files', '*'),
        ]
        f = tkFileDialog.askopenfile(filetypes=myFormats, mode='rb')
        if f is None:
            return
        self.newTopology()
        loadedTopology = json.load(f)

        # Load application preferences
        if 'application' in loadedTopology:
            self.appPrefs.update(loadedTopology['application'])
            if "ovsOf10" not in self.appPrefs["openFlowVersions"]:
                self.appPrefs["openFlowVersions"]["ovsOf10"] = '0'
            if "ovsOf11" not in self.appPrefs["openFlowVersions"]:
                self.appPrefs["openFlowVersions"]["ovsOf11"] = '0'
            if "ovsOf12" not in self.appPrefs["openFlowVersions"]:
                self.appPrefs["openFlowVersions"]["ovsOf12"] = '0'
            if "ovsOf13" not in self.appPrefs["openFlowVersions"]:
                self.appPrefs["openFlowVersions"]["ovsOf13"] = '0'
            if "sflow" not in self.appPrefs:
                self.appPrefs["sflow"] = self.sflowDefaults
            if "netflow" not in self.appPrefs:
                self.appPrefs["netflow"] = self.nflowDefaults

        # Load controllers
        if 'controllers' in loadedTopology:
            if loadedTopology['version'] == '1':
                # This is old location of controller info
                hostname = 'c0'
                self.controllers = {}
                self.controllers[hostname] = loadedTopology['controllers']['c0']
                self.controllers[hostname]['hostname'] = hostname
                self.addNode('Controller', 0, float(
                    30), float(30), name=hostname)
                icon = self.findWidgetByName(hostname)
                icon.bind('<Button-3>', self.do_controllerPopup)
            else:
                controllers = loadedTopology['controllers']
                for controller in controllers:
                    hostname = controller['opts']['hostname']
                    x = controller['x']
                    y = controller['y']
                    self.addNode('Controller', 0, float(x),
                                 float(y), name=hostname)
                    self.controllers[hostname] = controller['opts']
                    icon = self.findWidgetByName(hostname)
                    icon.bind('<Button-3>', self.do_controllerPopup)

        # Load hosts
        hosts = loadedTopology['hosts']
        for host in hosts:
            nodeNum = host['number']
            hostname = 'h'+nodeNum
            if 'hostname' in host['opts']:
                hostname = host['opts']['hostname']
            else:
                host['opts']['hostname'] = hostname
            if 'nodeNum' not in host['opts']:
                host['opts']['nodeNum'] = int(nodeNum)
            x = host['x']
            y = host['y']
            self.addNode('Host', nodeNum, float(x), float(y), name=hostname)

            # Fix JSON converting tuple to list when saving
            if 'privateDirectory' in host['opts']:
                newDirList = []
                for privateDir in host['opts']['privateDirectory']:
                    if isinstance(privateDir, list):
                        newDirList.append((privateDir[0], privateDir[1]))
                    else:
                        newDirList.append(privateDir)
                host['opts']['privateDirectory'] = newDirList
            self.hostOpts[hostname] = host['opts']
            icon = self.findWidgetByName(hostname)
            icon.bind('<Button-3>', self.do_hostPopup)

        # Load switches
        switches = loadedTopology['switches']
        for switch in switches:
            nodeNum = switch['number']
            hostname = 's'+nodeNum
            if 'controllers' not in switch['opts']:
                switch['opts']['controllers'] = []
            if 'switchType' not in switch['opts']:
                switch['opts']['switchType'] = 'default'
            if 'hostname' in switch['opts']:
                hostname = switch['opts']['hostname']
            else:
                switch['opts']['hostname'] = hostname
            if 'nodeNum' not in switch['opts']:
                switch['opts']['nodeNum'] = int(nodeNum)
            x = switch['x']
            y = switch['y']
            if switch['opts']['switchType'] == "legacyRouter":
                self.addNode('LegacyRouter', nodeNum,
                             float(x), float(y), name=hostname)
                icon = self.findWidgetByName(hostname)
                icon.bind('<Button-3>', self.do_legacyRouterPopup)
            elif switch['opts']['switchType'] == "legacySwitch":
                self.addNode('LegacySwitch', nodeNum,
                             float(x), float(y), name=hostname)
                icon = self.findWidgetByName(hostname)
                icon.bind('<Button-3>', self.do_legacySwitchPopup)
            else:
                self.addNode('Switch', nodeNum, float(x),
                             float(y), name=hostname)
                icon = self.findWidgetByName(hostname)
                icon.bind('<Button-3>', self.do_switchPopup)
            self.switchOpts[hostname] = switch['opts']

            # create links to controllers
            if int(loadedTopology['version']) > 1:
                controllers = self.switchOpts[hostname]['controllers']
                for controller in controllers:
                    dest = self.findWidgetByName(controller)
                    dx, dy = self.canvas.coords(self.widgetToItem[dest])
                    self.link = self.canvas.create_line(float(x),
                                                        float(y),
                                                        dx,
                                                        dy,
                                                        width=4,
                                                        fill='red',
                                                        dash=(6, 4, 2, 4),
                                                        tag='link')
                    c.itemconfig(self.link, tags=c.gettags(
                        self.link)+('control',))
                    self.addLink(icon, dest, linktype='control')
                    self.createControlLinkBindings()
                    self.link = self.linkWidget = None
            else:
                dest = self.findWidgetByName('c0')
                dx, dy = self.canvas.coords(self.widgetToItem[dest])
                self.link = self.canvas.create_line(float(x),
                                                    float(y),
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

        # Load links
        links = loadedTopology['links']
        for link in links:
            srcNode = link['src']
            src = self.findWidgetByName(srcNode)
            sx, sy = self.canvas.coords(self.widgetToItem[src])

            destNode = link['dest']
            dest = self.findWidgetByName(destNode)
            dx, dy = self.canvas.coords(self.widgetToItem[dest])

            self.link = self.canvas.create_line(sx, sy, dx, dy, width=4,
                                                fill='blue', tag='link')
            c.itemconfig(self.link, tags=c.gettags(self.link)+('data',))
            self.addLink(src, dest, linkopts=link['opts'])
            self.createDataLinkBindings()
            self.link = self.linkWidget = None

        f.close()

def addNode(self, node, nodeNum, x, y, name=None):
    "Add a new node to our canvas."
    if node == 'Switch':
        self.switchCount += 1
    if node == 'Host':
        self.hostCount += 1
    if node == 'Controller':
        self.controllerCount += 1
    if name is None:
        name = self.nodePrefixes[node] + nodeNum
    self.addNamedNode(node, name, x, y)

def addNamedNode(self, node, name, x, y):
    "Add a new node to our canvas."
    icon = self.nodeIcon(node, name)
    item = self.canvas.create_window(x, y, anchor='c', window=icon,
                                        tags=node)
    self.widgetToItem[icon] = item
    self.itemToWidget[item] = icon
    icon.links = {}