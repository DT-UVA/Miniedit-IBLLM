#!/usr/bin/env python

"""
Miniedit-IBLLM: a LLM based network editor for Mininet

This is a simple demonstration of how one might build a
GUI application using Mininet as the network model.
 
Basis framework by:
Bob Lantz, April 2010
Gregory Gee, July 2013

IBLLM extension by:
Dani Termaat, May 2025

Controller icon from http://semlabs.co.uk/
OpenFlow icon from https://www.opennetworking.org/
"""

import os
import sys

from mininet.log import info, setLogLevel
from mininet.term import cleanUpScreens

# Import Tkinter
from tkinter import (Frame, Menu, Wm)
from tkinter import font as tkFont

# Import the images
from modules.LLM.constants import LLM_TOOLS_TEXT_PROMPT
from modules.miniedit_utils.images import miniEditImages

# Import all the definitions
from modules.miniedit_utils.definitions import *

if 'PYTHONPATH' in os.environ:
    sys.path = os.environ['PYTHONPATH'].split(':') + sys.path


class MiniEdit(Frame):
    # Inline import of methods
    from modules.miniedit_utils.importer import parseArgs, importTopo
    from modules.miniedit_utils.exporter import exportScript, saveTopology

    # Generic node handlers
    from modules.handlers.generic_node_handlers import (createNodeBindings, selectItem, enterNode, leaveNode, clickNode, dragNode, releaseNode)
    from modules.handlers.specific_node_handlers import (selectNode, dragNodeAround, createControlLinkBindings, 
                                                         createDataLinkBindings, startLink, finishLink, about, createToolImages)

    # Menubar
    from modules.handlers.menubar import createMenubar

    # Canvas bindings
    from modules.handlers.canvas_binding import (clickSelect, deleteItem, deleteSelection, nodeIcon, newNode, clickController, 
                                                 clickHost, clickLegacyRouter, clickLegacySwitch, clickSwitch, dragNetLink, releaseNetLink,
                                                 createCanvas, updateScrollRegion, canvasx, canvasy, canvasHandle, clickCanvas, dragCanvas,
                                                 releaseCanvas, findItem, activate)
    # Topology loader 
    from modules.miniedit_utils.load_topology import loadTopology, addNode, addNamedNode

    # Popups
    from modules.handlers.popups import (do_linkPopup, do_controllerPopup, do_legacyRouterPopup, do_hostPopup, do_legacySwitchPopup, do_switchPopup)

    # Toolbar
    from modules.handlers.toolbar import createToolTip, createToolbar, findWidgetByName, newTopology

    # API interfaces
    from modules.api_interfaces.configurators import (checkIntf, hostDetails, switchDetails, linkUp, linkDown, 
                                                      linkDetails, prefDetails, controllerDetails, listBridge, 
                                                      addLink, deleteLink, deleteNode, buildNodes, buildLinks,
                                                      pathCheck, build, postStartSetup)
    
    # Tools
    from modules.handlers.tools import (xterm, iperf, ovsShow, rootTerminal)
    from modules.helpers.find_by_name import find_widget_by_name

    # LLM section
    from modules.LLM.llm_chat import LLMChat, update_state_button
    from modules.LLM.functions.multimodal_layer import analyse_image
    from modules.LLM.chatwindow import create_chat_window, submit_chat, upload_image
    from modules.LLM.testing.executor import llm_text_test_generation, llm_image_test_generation

    # LLM functions
    from modules.LLM.functions.node_operations import add_node_LLM, delete_node_LLM, update_node_location_LLM, update_host_settings_LLM
    from modules.LLM.functions.context_gathering import get_nodes, get_coordinates, get_links, get_context
    from modules.LLM.functions.link_operations import add_link_LLM, remove_link_LLM, update_link_settings_LLM, update_link_settings_LLM

    def __init__(self, parent=None, cheight=600, cwidth=1000):
        self.defaultIpBase = '10.0.0.0/8'

        self.nflowDefaults = {'nflowTarget': '',
                              'nflowTimeout': '600',
                              'nflowAddId': '0'}
        self.sflowDefaults = {'sflowTarget': '',
                              'sflowSampling': '400',
                              'sflowHeader': '128',
                              'sflowPolling': '30'}

        self.appPrefs = {
            "ipBase": self.defaultIpBase,
            "startCLI": "0",
            "terminalType": 'xterm',
            "switchType": 'ovs',
            "dpctl": '',
            'sflow': self.sflowDefaults,
            'netflow': self.nflowDefaults,
            'openFlowVersions': {'ovsOf10': '1',
                                 'ovsOf11': '0',
                                 'ovsOf12': '0',
                                 'ovsOf13': '0'}

        }

        Frame.__init__(self, parent)
        self.action = None
        self.appName = 'MiniEdit-IBLLM'
        self.fixedFont = tkFont.Font(family="DejaVu Sans Mono", size="14")

        # Initialize the chat history with the system prompt
        self.chat_history = [
            {'role': 'system', 'content': LLM_TOOLS_TEXT_PROMPT},
        ]

        # Style
        self.font = ('Geneva', 9)
        self.smallFont = ('Geneva', 7)
        self.bg = 'white'

        # Title
        self.top = self.winfo_toplevel()
        self.top.title(self.appName)

        # Menu bar
        self.createMenubar()

        self.store_context = False

        # Editing canvas
        self.cheight, self.cwidth = cheight, cwidth
        self.cframe, self.canvas = self.createCanvas()

        # Chatwindow
        self.chatFrame = self.create_chat_window()


        # Toolbar
        self.controllers = {}

        # Toolbar
        self.images = miniEditImages()
        self.buttons = {}
        self.active = None
        self.tools = ('Select', 'Host', 'Switch', 'LegacySwitch',
                      'LegacyRouter', 'NetLink', 'Controller')
        self.customColors = {'Switch': 'darkGreen', 'Host': 'blue'}
        self.toolbar = self.createToolbar()

        # Layout
        self.toolbar.grid(column=0, row=0, sticky='nsew')
        self.cframe.grid(column=1, row=0)
        self.chatFrame.grid(column=2, row=0, sticky='nsew')
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.pack(expand=True, fill='both')

        # About box
        self.aboutBox = None

        # Initialize node data
        self.nodeBindings = self.createNodeBindings()
        self.nodePrefixes = {'LegacyRouter': 'R', 'LegacySwitch': 'LS',
                             'Switch': 'S', 'Host': 'H', 'Controller': 'C'}
        self.widgetToItem = {}
        self.itemToWidget = {}

        # Initialize link tool
        self.link = self.linkWidget = None

        # Selection support
        self.selection = None

        # Keyboard bindings
        self.bind('<Control-q>', lambda event: self.quit())
        self.bind('<KeyPress-Delete>', self.deleteSelection)
        self.bind('<KeyPress-BackSpace>', self.deleteSelection)
        self.focus()

        self.hostPopup = Menu(self.top, tearoff=0)
        self.hostPopup.add_command(label='Host Options', font=self.font)
        self.hostPopup.add_separator()
        self.hostPopup.add_command(
            label='Properties', font=self.font, command=self.hostDetails)

        self.hostRunPopup = Menu(self.top, tearoff=0)
        self.hostRunPopup.add_command(label='Host Options', font=self.font)
        self.hostRunPopup.add_separator()
        self.hostRunPopup.add_command(
            label='Terminal', font=self.font, command=self.xterm)

        self.legacyRouterRunPopup = Menu(self.top, tearoff=0)
        self.legacyRouterRunPopup.add_command(
            label='Router Options', font=self.font)
        self.legacyRouterRunPopup.add_separator()
        self.legacyRouterRunPopup.add_command(
            label='Terminal', font=self.font, command=self.xterm)

        self.switchPopup = Menu(self.top, tearoff=0)
        self.switchPopup.add_command(label='Switch Options', font=self.font)
        self.switchPopup.add_separator()
        self.switchPopup.add_command(
            label='Properties', font=self.font, command=self.switchDetails)

        self.switchRunPopup = Menu(self.top, tearoff=0)
        self.switchRunPopup.add_command(label='Switch Options', font=self.font)
        self.switchRunPopup.add_separator()
        self.switchRunPopup.add_command(
            label='List bridge details', font=self.font, command=self.listBridge)

        self.linkPopup = Menu(self.top, tearoff=0)
        self.linkPopup.add_command(label='Link Options', font=self.font)
        self.linkPopup.add_separator()
        self.linkPopup.add_command(
            label='Properties', font=self.font, command=self.linkDetails)

        self.linkRunPopup = Menu(self.top, tearoff=0)
        self.linkRunPopup.add_command(label='Link Options', font=self.font)
        self.linkRunPopup.add_separator()
        self.linkRunPopup.add_command(
            label='Link Up', font=self.font, command=self.linkUp)
        self.linkRunPopup.add_command(
            label='Link Down', font=self.font, command=self.linkDown)

        self.controllerPopup = Menu(self.top, tearoff=0)
        self.controllerPopup.add_command(
            label='Controller Options', font=self.font)
        self.controllerPopup.add_separator()
        self.controllerPopup.add_command(
            label='Properties', font=self.font, command=self.controllerDetails)

        # Event handling initalization
        self.linkx = self.linky = self.linkItem = None
        self.lastSelection = None

        # Model initialization
        self.links = {}
        self.hostOpts = {}
        self.switchOpts = {}
        self.hostCount = 0
        self.switchCount = 0
        self.controllerCount = 0
        self.net = None

        # Close window gracefully
        Wm.wm_protocol(self.top, name='WM_DELETE_WINDOW', func=self.quit)

    def quit(self):
        "Stop our network, if any, then quit."
        self.stop()
        Frame.quit(self)

    def doRun(self):
        "Run command."
        self.activate('Select')
        for tool in self.tools:
            self.buttons[tool].config(state='disabled')
        self.start()

    def doStop(self):
        "Stop command."
        self.stop()
        for tool in self.tools:
            self.buttons[tool].config(state='normal')

    def start(self):
        "Start network."
        if self.net is None:
            self.net = self.build()

            info('**** Starting %s controllers\n' % len(self.net.controllers))
            for controller in self.net.controllers:
                info(str(controller) + ' ')
                controller.start()
            info('\n')
            info('**** Starting %s switches\n' % len(self.net.switches))
            for widget, item in self.widgetToItem.items():
                name = widget['text']
                tags = self.canvas.gettags(item)
                if 'Switch' in tags:
                    opts = self.switchOpts[name]
                    switchControllers = []
                    for ctrl in opts['controllers']:
                        switchControllers.append(self.net.get(ctrl))
                    info(name + ' ')
                    # Figure out what controllers will manage this switch
                    self.net.get(name).start(switchControllers)
                if 'LegacySwitch' in tags:
                    self.net.get(name).start([])
                    info(name + ' ')
            info('\n')

            self.postStartSetup()

    def stop(self):
        "Stop network."
        if self.net is not None:
            # Stop host details
            for widget, item in self.widgetToItem.items():
                name = widget['text']
                tags = self.canvas.gettags(item)
                if 'Host' in tags:
                    newHost = self.net.get(name)
                    opts = self.hostOpts[name]
                    # Run User Defined Stop Command
                    if 'stopCommand' in opts:
                        newHost.cmdPrint(opts['stopCommand'])
                if 'Switch' in tags:
                    newNode = self.net.get(name)
                    opts = self.switchOpts[name]
                    # Run User Defined Stop Command
                    if 'stopCommand' in opts:
                        newNode.cmdPrint(opts['stopCommand'])

            self.net.stop()
        cleanUpScreens()
        self.net = None



if __name__ == '__main__':
    setLogLevel('info')
    app = MiniEdit()
    app.parseArgs()
    app.importTopo()
    app.mainloop()
