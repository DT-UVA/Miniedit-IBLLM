from tkinter import Label


def createNodeBindings(self):
    "Create a set of bindings for nodes."
    bindings = {
        '<ButtonPress-1>': self.clickNode,
        '<B1-Motion>': self.dragNode,
        '<ButtonRelease-1>': self.releaseNode,
        '<Enter>': self.enterNode,
        '<Leave>': self.leaveNode
    }
    l = Label()  # lightweight-ish owner for bindings
    for event, binding in bindings.items():
        l.bind(event, binding)
    return l

def selectItem(self, item):
    "Select an item and remember old selection."
    self.lastSelection = self.selection
    self.selection = item

def enterNode(self, event):
    "Select node on entry."
    self.selectNode(event)

def leaveNode(self, _event):
    "Restore old selection on exit."
    self.selectItem(self.lastSelection)

def clickNode(self, event):
    "Node click handler."
    if self.active == 'NetLink':
        self.startLink(event)
    else:
        self.selectNode(event)
    return 'break'

def dragNode(self, event):
    "Node drag handler."
    if self.active == 'NetLink':
        self.dragNetLink(event)
    else:
        self.dragNodeAround(event)

def releaseNode(self, event):
    "Node release handler."
    if self.active == 'NetLink':
        self.finishLink(event)