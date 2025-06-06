from functools import partial

# Import Tkinter
from tkinter import (Frame, Label, Button)

# Import all the dialogs
from modules.dialogs.tooltip import ToolTip

# Toolbar
@staticmethod
def createToolTip(widget, text):
    toolTip = ToolTip(widget)

    def enter(_event):
        toolTip.showtip(text)

    def leave(_event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

def createToolbar(self):
    "Create and return our toolbar frame."

    toolbar = Frame(self)

    # Tools
    for tool in self.tools:
        cmd = partial(self.activate, tool)
        b = Button(toolbar, text=tool, font=self.smallFont, command=cmd)
        if tool in self.images:
            b.config(height=35, image=self.images[tool])
            self.createToolTip(b, str(tool))
            # b.config( compound='top' )
        b.pack(fill='x')
        self.buttons[tool] = b
    self.activate(self.tools[0])

    # Spacer
    Label(toolbar, text='').pack()

    # Commands
    for cmd, color in [('Stop', 'darkRed'), ('Run', 'darkGreen')]:
        doCmd = getattr(self, 'do' + cmd)
        b = Button(toolbar, text=cmd, font=self.smallFont,
                    fg=color, command=doCmd)
        b.pack(fill='x', side='bottom')

    return toolbar

def findWidgetByName(self, name):
    for widget in self.widgetToItem:
        if name == widget['text']:
            return widget
    return None

def newTopology(self):
    "New command."
    for widget in tuple(self.widgetToItem):
        self.deleteItem(self.widgetToItem[widget])
    self.hostCount = 0
    self.switchCount = 0
    self.controllerCount = 0
    self.links = {}
    self.hostOpts = {}
    self.switchOpts = {}
    self.controllers = {}
    self.appPrefs["ipBase"] = self.defaultIpBase