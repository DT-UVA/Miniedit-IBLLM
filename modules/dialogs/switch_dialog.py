from modules.dialogs.custom_dialog import CustomDialog
from mininet.util import StrictVersion
from tkinter.messagebox import showerror
from mininet.net import VERSION
from tkinter import (Frame, Label, Entry, OptionMenu,
                     Checkbutton, Button, StringVar, IntVar, E, W)
import re

from modules.dialogs.vertical_scroll_table import VerticalScrolledTable
from modules.miniedit_utils.definitions import MININET_VERSION


class SwitchDialog(CustomDialog):

    def __init__(self, master, title, prefDefaults):

        self.prefValues = prefDefaults
        self.result = None
        CustomDialog.__init__(self, master, title)

    def body(self, master):
        self.rootFrame = master
        self.leftfieldFrame = Frame(self.rootFrame)
        self.rightfieldFrame = Frame(self.rootFrame)
        self.leftfieldFrame.grid(row=0, column=0, sticky='nswe')
        self.rightfieldFrame.grid(row=0, column=1, sticky='nswe')

        rowCount = 0
        externalInterfaces = []
        if 'externalInterfaces' in self.prefValues:
            externalInterfaces = self.prefValues['externalInterfaces']

        # Field for Hostname
        Label(self.leftfieldFrame, text="Hostname:").grid(
            row=rowCount, sticky=E)
        self.hostnameEntry = Entry(self.leftfieldFrame)
        self.hostnameEntry.grid(row=rowCount, column=1)
        self.hostnameEntry.insert(0, self.prefValues['hostname'])
        rowCount += 1

        # Field for DPID
        Label(self.leftfieldFrame, text="DPID:").grid(row=rowCount, sticky=E)
        self.dpidEntry = Entry(self.leftfieldFrame)
        self.dpidEntry.grid(row=rowCount, column=1)
        if 'dpid' in self.prefValues:
            self.dpidEntry.insert(0, self.prefValues['dpid'])
        rowCount += 1

        # Field for Netflow
        Label(self.leftfieldFrame, text="Enable NetFlow:").grid(
            row=rowCount, sticky=E)
        self.nflow = IntVar()
        self.nflowButton = Checkbutton(
            self.leftfieldFrame, variable=self.nflow)
        self.nflowButton.grid(row=rowCount, column=1, sticky=W)
        if 'netflow' in self.prefValues:
            if self.prefValues['netflow'] == '0':
                self.nflowButton.deselect()
            else:
                self.nflowButton.select()
        else:
            self.nflowButton.deselect()
        rowCount += 1

        # Field for sflow
        Label(self.leftfieldFrame, text="Enable sFlow:").grid(
            row=rowCount, sticky=E)
        self.sflow = IntVar()
        self.sflowButton = Checkbutton(
            self.leftfieldFrame, variable=self.sflow)
        self.sflowButton.grid(row=rowCount, column=1, sticky=W)
        if 'sflow' in self.prefValues:
            if self.prefValues['sflow'] == '0':
                self.sflowButton.deselect()
            else:
                self.sflowButton.select()
        else:
            self.sflowButton.deselect()
        rowCount += 1

        # Selection of switch type
        Label(self.leftfieldFrame, text="Switch Type:").grid(
            row=rowCount, sticky=E)
        self.switchType = StringVar(self.leftfieldFrame)
        self.switchTypeMenu = OptionMenu(self.leftfieldFrame, self.switchType, "Default", "Open vSwitch Kernel Mode",
                                         "Indigo Virtual Switch", "Userspace Switch", "Userspace Switch inNamespace")
        self.switchTypeMenu.grid(row=rowCount, column=1, sticky=W)
        if 'switchType' in self.prefValues:
            switchTypePref = self.prefValues['switchType']
            if switchTypePref == 'ivs':
                self.switchType.set("Indigo Virtual Switch")
            elif switchTypePref == 'userns':
                self.switchType.set("Userspace Switch inNamespace")
            elif switchTypePref == 'user':
                self.switchType.set("Userspace Switch")
            elif switchTypePref == 'ovs':
                self.switchType.set("Open vSwitch Kernel Mode")
            else:
                self.switchType.set("Default")
        else:
            self.switchType.set("Default")
        rowCount += 1

        # Field for Switch IP
        Label(self.leftfieldFrame, text="IP Address:").grid(
            row=rowCount, sticky=E)
        self.ipEntry = Entry(self.leftfieldFrame)
        self.ipEntry.grid(row=rowCount, column=1)
        if 'switchIP' in self.prefValues:
            self.ipEntry.insert(0, self.prefValues['switchIP'])
        rowCount += 1

        # Field for DPCTL port
        Label(self.leftfieldFrame, text="DPCTL port:").grid(
            row=rowCount, sticky=E)
        self.dpctlEntry = Entry(self.leftfieldFrame)
        self.dpctlEntry.grid(row=rowCount, column=1)
        if 'dpctl' in self.prefValues:
            self.dpctlEntry.insert(0, self.prefValues['dpctl'])
        rowCount += 1

        # External Interfaces
        Label(self.rightfieldFrame, text="External Interface:").grid(
            row=0, sticky=E)
        self.b = Button(self.rightfieldFrame, text='Add',
                        command=self.addInterface)
        self.b.grid(row=0, column=1)

        self.interfaceFrame = VerticalScrolledTable(
            self.rightfieldFrame, rows=0, columns=1, title='External Interfaces')
        self.interfaceFrame.grid(row=1, column=0, sticky='nswe', columnspan=2)
        self.tableFrame = self.interfaceFrame.interior

        # Add defined interfaces
        for externalInterface in externalInterfaces:
            self.tableFrame.addRow(value=[externalInterface])

        self.commandFrame = Frame(self.rootFrame)
        self.commandFrame.grid(row=1, column=0, sticky='nswe', columnspan=2)
        self.commandFrame.columnconfigure(1, weight=1)
        # Start command
        Label(self.commandFrame, text="Start Command:").grid(
            row=0, column=0, sticky=W)
        self.startEntry = Entry(self.commandFrame)
        self.startEntry.grid(row=0, column=1,  sticky='nsew')
        if 'startCommand' in self.prefValues:
            self.startEntry.insert(0, str(self.prefValues['startCommand']))
        # Stop command
        Label(self.commandFrame, text="Stop Command:").grid(
            row=1, column=0, sticky=W)
        self.stopEntry = Entry(self.commandFrame)
        self.stopEntry.grid(row=1, column=1, sticky='nsew')
        if 'stopCommand' in self.prefValues:
            self.stopEntry.insert(0, str(self.prefValues['stopCommand']))

    def addInterface(self):
        self.tableFrame.addRow()

    def defaultDpid(self, name):
        "Derive dpid from switch name, s1 -> 1"
        assert self  # satisfy pylint and allow contextual override
        try:
            dpid = int(re.findall(r'\d+', name)[0])
            dpid = hex(dpid)[2:]
            return dpid
        except IndexError:
            return None
            # raise Exception( 'Unable to derive default datapath ID - '
            #                 'please either specify a dpid or use a '
            #                 'canonical switch name such as s23.' )

    def apply(self):
        externalInterfaces = []
        for row in range(self.tableFrame.rows):
            # debug( 'Interface is ' + self.tableFrame.get(row, 0), '\n' )
            if len(self.tableFrame.get(row, 0)) > 0:
                externalInterfaces.append(self.tableFrame.get(row, 0))

        dpid = self.dpidEntry.get()
        if (self.defaultDpid(self.hostnameEntry.get()) is None
           and len(dpid) == 0):
            showerror(title="Error",
                      message='Unable to derive default datapath ID - '
                      'please either specify a DPID or use a '
                      'canonical switch name such as s23.')

        results = {'externalInterfaces': externalInterfaces,
                   'hostname': self.hostnameEntry.get(),
                   'dpid': dpid,
                   'startCommand': self.startEntry.get(),
                   'stopCommand': self.stopEntry.get(),
                   'sflow': str(self.sflow.get()),
                   'netflow': str(self.nflow.get()),
                   'dpctl': self.dpctlEntry.get(),
                   'switchIP': self.ipEntry.get()}
        sw = self.switchType.get()
        if sw == 'Indigo Virtual Switch':
            results['switchType'] = 'ivs'
            if StrictVersion(MININET_VERSION) < StrictVersion('2.1'):
                self.ovsOk = False
                showerror(title="Error",
                          message='MiniNet version 2.1+ required. You have '+VERSION+'.')
        elif sw == 'Userspace Switch inNamespace':
            results['switchType'] = 'userns'
        elif sw == 'Userspace Switch':
            results['switchType'] = 'user'
        elif sw == 'Open vSwitch Kernel Mode':
            results['switchType'] = 'ovs'
        else:
            results['switchType'] = 'default'
        self.result = results
