# Import Tkinter
from tkinter import (Frame, Label, Button, Canvas, Scrollbar)


def clickSelect(self, event):
    "Select an item."
    self.selectItem(self.findItem(event.x, event.y))


def deleteItem(self, item):
    "Delete an item."
    # Don't delete while network is running
    if self.buttons['Select']['state'] == 'disabled':
        return
    # Delete from model
    if item in self.links:
        self.deleteLink(item)
    if item in self.itemToWidget:
        self.deleteNode(item)
    # Delete from view
    self.canvas.delete(item)


def deleteSelection(self, _event):
    "Delete the selected item."
    if self.selection is not None:
        self.deleteItem(self.selection)
    self.selectItem(None)


def nodeIcon(self, node, name):
    "Create a new node icon."
    icon = Button(self.canvas, image=self.images[node],
                  text=name, compound='top')
    # Unfortunately bindtags wants a tuple
    bindtags = [str(self.nodeBindings)]
    bindtags += list(icon.bindtags())
    icon.bindtags(tuple(bindtags))
    return icon


def newNode(self, node, event, hostname=None):
    "Add a new node to our canvas."
    c = self.canvas
    x, y = c.canvasx(event.x), c.canvasy(event.y)

    if hostname is not None:
        name = hostname
    else:
        name = self.nodePrefixes[node]
    
    if node == 'Switch':
        self.switchCount += 1

        # If a hostname is provided, use it
        if hostname is None:
            name = self.nodePrefixes[node] + str(self.switchCount)

        # Create the switch entry
        self.switchOpts[name] = {}
        self.switchOpts[name]['nodeNum'] = self.switchCount
        self.switchOpts[name]['hostname'] = name
        self.switchOpts[name]['switchType'] = 'default'
        self.switchOpts[name]['controllers'] = []

    if node == 'LegacyRouter':
        self.switchCount += 1

        if hostname is None:
            name = self.nodePrefixes[node] + str(self.switchCount)

        # Create the router entry
        self.switchOpts[name] = {}
        self.switchOpts[name]['nodeNum'] = self.switchCount
        self.switchOpts[name]['hostname'] = name
        self.switchOpts[name]['switchType'] = 'legacyRouter'

    if node == 'LegacySwitch':
        self.switchCount += 1

        if hostname is None:
            name = self.nodePrefixes[node] + str(self.switchCount)

        # Create the switch entry
        self.switchOpts[name] = {}
        self.switchOpts[name]['nodeNum'] = self.switchCount
        self.switchOpts[name]['hostname'] = name
        self.switchOpts[name]['switchType'] = 'legacySwitch'
        self.switchOpts[name]['controllers'] = []

    if node == 'Host':
        self.hostCount += 1

        if hostname is None:
            name = self.nodePrefixes[node] + str(self.hostCount)

        # Create the host entry
        self.hostOpts[name] = {'sched': 'host'}
        self.hostOpts[name]['nodeNum'] = self.hostCount
        self.hostOpts[name]['hostname'] = name

    if node == 'Controller':
        if hostname is None:
            name = self.nodePrefixes[node] + str(self.controllerCount)

        ctrlr = {'controllerType': 'ref',
                 'hostname': name,
                 'controllerProtocol': 'tcp',
                 'remoteIP': '127.0.0.1',
                 'remotePort': 6633}
        self.controllers[name] = ctrlr
        # We want to start controller count at 0
        self.controllerCount += 1

    icon = self.nodeIcon(node, name)
    item = self.canvas.create_window(x, y, anchor='c', window=icon, tags=node)
    self.widgetToItem[icon] = item
    self.itemToWidget[item] = icon
    self.selectItem(item)

    icon.links = {}
    if node == 'Switch':
        icon.bind('<Button-3>', self.do_switchPopup)
    if node == 'LegacyRouter':
        icon.bind('<Button-3>', self.do_legacyRouterPopup)
    if node == 'LegacySwitch':
        icon.bind('<Button-3>', self.do_legacySwitchPopup)
    if node == 'Host':
        icon.bind('<Button-3>', self.do_hostPopup)
    if node == 'Controller':
        icon.bind('<Button-3>', self.do_controllerPopup)


def clickController(self, event):
    "Add a new Controller to our canvas."
    self.newNode('Controller', event)


def clickHost(self, event):
    "Add a new host to our canvas."
    self.newNode('Host', event)


def clickLegacyRouter(self, event):
    "Add a new switch to our canvas."
    self.newNode('LegacyRouter', event)


def clickLegacySwitch(self, event):
    "Add a new switch to our canvas."
    self.newNode('LegacySwitch', event)


def clickSwitch(self, event):
    "Add a new switch to our canvas."
    self.newNode('Switch', event)


def dragNetLink(self, event):
    "Drag a link's endpoint to another node."
    if self.link is None:
        return
    # Since drag starts in widget, we use root coords
    x = self.canvasx(event.x_root)
    y = self.canvasy(event.y_root)
    c = self.canvas
    c.coords(self.link, self.linkx, self.linky, x, y)


def releaseNetLink(self, _event):
    "Give up on the current link."
    if self.link is not None:
        self.canvas.delete(self.link)
    self.linkWidget = self.linkItem = self.link = None


def createCanvas(self):
    "Create and return our scrolling canvas frame."
    f = Frame(self)

    canvas = Canvas(f, width=self.cwidth, height=self.cheight,
                    bg=self.bg)

    # Scroll bars
    xbar = Scrollbar(f, orient='horizontal', command=canvas.xview)
    ybar = Scrollbar(f, orient='vertical', command=canvas.yview)
    canvas.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)

    # Resize box
    resize = Label(f, bg='white')

    # Layout
    canvas.grid(row=0, column=1, sticky='nsew')
    ybar.grid(row=0, column=2, sticky='ns')
    xbar.grid(row=1, column=1, sticky='ew')
    resize.grid(row=1, column=2, sticky='nsew')

    # Resize behavior
    f.rowconfigure(0, weight=1)
    f.columnconfigure(1, weight=1)
    f.grid(row=0, column=0, sticky='nsew')
    f.bind('<Configure>', lambda event: self.updateScrollRegion())

    # Mouse bindings
    canvas.bind('<ButtonPress-1>', self.clickCanvas)
    canvas.bind('<B1-Motion>', self.dragCanvas)
    canvas.bind('<ButtonRelease-1>', self.releaseCanvas)

    return f, canvas


def updateScrollRegion(self):
    "Update canvas scroll region to hold everything."
    bbox = self.canvas.bbox('all')
    if bbox is not None:
        self.canvas.configure(scrollregion=(0, 0, bbox[2], bbox[3]))


def canvasx(self, x_root):
    "Convert root x coordinate to canvas coordinate."
    c = self.canvas
    return c.canvasx(x_root) - c.winfo_rootx()


def canvasy(self, y_root):
    "Convert root y coordinate to canvas coordinate."
    c = self.canvas
    return c.canvasy(y_root) - c.winfo_rooty()


def canvasHandle(self, eventName, event):
    "Generic canvas event handler"
    if self.active is None:
        return
    toolName = self.active
    handler = getattr(self, eventName + toolName, None)
    if handler is not None:
        handler(event)


def clickCanvas(self, event):
    "Canvas click handler."
    self.canvasHandle('click', event)


def dragCanvas(self, event):
    "Canvas drag handler."
    self.canvasHandle('drag', event)


def releaseCanvas(self, event):
    "Canvas mouse up handler."
    self.canvasHandle('release', event)


def findItem(self, x, y):
    "Find items at a location in our canvas."
    items = self.canvas.find_overlapping(x, y, x, y)
    if len(items) == 0:
        return None
    else:
        return items[0]


def activate(self, toolName):
    "Activate a tool and press its button."
    # Adjust button appearance
    if self.active:
        self.buttons[self.active].configure(relief='raised')
    self.buttons[toolName].configure(relief='sunken')
    # Activate dynamic bindings
    self.active = toolName
