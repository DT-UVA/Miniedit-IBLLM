from tkinter.ttk import Notebook
from tkinter import (Frame, Label, Entry, OptionMenu,
                     Button, StringVar, E, W, EW, NW, Y, VERTICAL, SOLID,
                     CENTER, RIGHT, LEFT, BOTH, TRUE, FALSE)

from modules.dialogs.custom_dialog import CustomDialog
from modules.dialogs.vertical_scroll_table import VerticalScrolledTable


class HostDialog(CustomDialog):

    def __init__(self, master, title, prefDefaults):

        self.prefValues = prefDefaults
        self.result = None

        CustomDialog.__init__(self, master, title)

    def body(self, master):
        self.rootFrame = master
        n = Notebook(self.rootFrame)
        self.propFrame = Frame(n)
        self.vlanFrame = Frame(n)
        self.interfaceFrame = Frame(n)
        self.mountFrame = Frame(n)
        n.add(self.propFrame, text='Properties')
        n.add(self.vlanFrame, text='VLAN Interfaces')
        n.add(self.interfaceFrame, text='External Interfaces')
        n.add(self.mountFrame, text='Private Directories')
        n.pack()

        # TAB 1
        # Field for Hostname
        Label(self.propFrame, text="Hostname:").grid(row=0, sticky=E)
        self.hostnameEntry = Entry(self.propFrame)
        self.hostnameEntry.grid(row=0, column=1)
        if 'hostname' in self.prefValues:
            self.hostnameEntry.insert(0, self.prefValues['hostname'])

        # Field for Switch IP
        Label(self.propFrame, text="IP Address:").grid(row=1, sticky=E)
        self.ipEntry = Entry(self.propFrame)
        self.ipEntry.grid(row=1, column=1)
        if 'ip' in self.prefValues:
            self.ipEntry.insert(0, self.prefValues['ip'])

        # Field for default route
        Label(self.propFrame, text="Default Route:").grid(row=2, sticky=E)
        self.routeEntry = Entry(self.propFrame)
        self.routeEntry.grid(row=2, column=1)
        if 'defaultRoute' in self.prefValues:
            self.routeEntry.insert(0, self.prefValues['defaultRoute'])

        # Field for CPU
        Label(self.propFrame, text="Amount CPU:").grid(row=3, sticky=E)
        self.cpuEntry = Entry(self.propFrame)
        self.cpuEntry.grid(row=3, column=1)
        if 'cpu' in self.prefValues:
            self.cpuEntry.insert(0, str(self.prefValues['cpu']))
        # Selection of Scheduler
        if 'sched' in self.prefValues:
            sched = self.prefValues['sched']
        else:
            sched = 'host'
        self.schedVar = StringVar(self.propFrame)
        self.schedOption = OptionMenu(
            self.propFrame, self.schedVar, "host", "cfs", "rt")
        self.schedOption.grid(row=3, column=2, sticky=W)
        self.schedVar.set(sched)

        # Selection of Cores
        Label(self.propFrame, text="Cores:").grid(row=4, sticky=E)
        self.coreEntry = Entry(self.propFrame)
        self.coreEntry.grid(row=4, column=1)
        if 'cores' in self.prefValues:
            self.coreEntry.insert(1, self.prefValues['cores'])

        # Start command
        Label(self.propFrame, text="Start Command:").grid(row=5, sticky=E)
        self.startEntry = Entry(self.propFrame)
        self.startEntry.grid(row=5, column=1, sticky='nswe', columnspan=3)
        if 'startCommand' in self.prefValues:
            self.startEntry.insert(0, str(self.prefValues['startCommand']))
        # Stop command
        Label(self.propFrame, text="Stop Command:").grid(row=6, sticky=E)
        self.stopEntry = Entry(self.propFrame)
        self.stopEntry.grid(row=6, column=1, sticky='nswe', columnspan=3)
        if 'stopCommand' in self.prefValues:
            self.stopEntry.insert(0, str(self.prefValues['stopCommand']))

        # TAB 2
        # External Interfaces
        self.externalInterfaces = 0
        Label(self.interfaceFrame, text="External Interface:").grid(
            row=0, column=0, sticky=E)
        self.b = Button(self.interfaceFrame, text='Add',
                        command=self.addInterface)
        self.b.grid(row=0, column=1)

        self.interfaceFrame = VerticalScrolledTable(
            self.interfaceFrame, rows=0, columns=1, title='External Interfaces')
        self.interfaceFrame.grid(row=1, column=0, sticky='nswe', columnspan=2)
        self.tableFrame = self.interfaceFrame.interior
        self.tableFrame.addRow(value=['Interface Name'], readonly=True)

        # Add defined interfaces
        externalInterfaces = []
        if 'externalInterfaces' in self.prefValues:
            externalInterfaces = self.prefValues['externalInterfaces']

        for externalInterface in externalInterfaces:
            self.tableFrame.addRow(value=[externalInterface])

        # TAB 3
        # VLAN Interfaces
        self.vlanInterfaces = 0
        Label(self.vlanFrame, text="VLAN Interface:").grid(
            row=0, column=0, sticky=E)
        self.vlanButton = Button(
            self.vlanFrame, text='Add', command=self.addVlanInterface)
        self.vlanButton.grid(row=0, column=1)

        self.vlanFrame = VerticalScrolledTable(
            self.vlanFrame, rows=0, columns=2, title='VLAN Interfaces')
        self.vlanFrame.grid(row=1, column=0, sticky='nswe', columnspan=2)
        self.vlanTableFrame = self.vlanFrame.interior
        self.vlanTableFrame.addRow(
            value=['IP Address', 'VLAN ID'], readonly=True)

        vlanInterfaces = []
        if 'vlanInterfaces' in self.prefValues:
            vlanInterfaces = self.prefValues['vlanInterfaces']
        for vlanInterface in vlanInterfaces:
            self.vlanTableFrame.addRow(value=vlanInterface)

        # TAB 4
        # Private Directories
        self.privateDirectories = 0
        Label(self.mountFrame, text="Private Directory:").grid(
            row=0, column=0, sticky=E)
        self.mountButton = Button(
            self.mountFrame, text='Add', command=self.addDirectory)
        self.mountButton.grid(row=0, column=1)

        self.mountFrame = VerticalScrolledTable(
            self.mountFrame, rows=0, columns=2, title='Directories')
        self.mountFrame.grid(row=1, column=0, sticky='nswe', columnspan=2)
        self.mountTableFrame = self.mountFrame.interior
        self.mountTableFrame.addRow(
            value=['Mount', 'Persistent Directory'], readonly=True)

        directoryList = []
        if 'privateDirectory' in self.prefValues:
            directoryList = self.prefValues['privateDirectory']
        for privateDir in directoryList:
            if isinstance(privateDir, tuple):
                self.mountTableFrame.addRow(value=privateDir)
            else:
                self.mountTableFrame.addRow(value=[privateDir, ''])

    def addDirectory(self):
        self.mountTableFrame.addRow()

    def addVlanInterface(self):
        self.vlanTableFrame.addRow()

    def addInterface(self):
        self.tableFrame.addRow()

    def apply(self):
        externalInterfaces = []
        for row in range(self.tableFrame.rows):
            if (len(self.tableFrame.get(row, 0)) > 0 and
                    row > 0):
                externalInterfaces.append(self.tableFrame.get(row, 0))
        vlanInterfaces = []
        for row in range(self.vlanTableFrame.rows):
            if (len(self.vlanTableFrame.get(row, 0)) > 0 and
                len(self.vlanTableFrame.get(row, 1)) > 0 and
                    row > 0):
                vlanInterfaces.append([self.vlanTableFrame.get(
                    row, 0), self.vlanTableFrame.get(row, 1)])
        privateDirectories = []
        for row in range(self.mountTableFrame.rows):
            if len(self.mountTableFrame.get(row, 0)) > 0 and row > 0:
                if len(self.mountTableFrame.get(row, 1)) > 0:
                    privateDirectories.append((self.mountTableFrame.get(
                        row, 0), self.mountTableFrame.get(row, 1)))
                else:
                    privateDirectories.append(self.mountTableFrame.get(row, 0))

        results = {'cpu': self.cpuEntry.get(),
                   'cores': self.coreEntry.get(),
                   'sched': self.schedVar.get(),
                   'hostname': self.hostnameEntry.get(),
                   'ip': self.ipEntry.get(),
                   'defaultRoute': self.routeEntry.get(),
                   'startCommand': self.startEntry.get(),
                   'stopCommand': self.stopEntry.get(),
                   'privateDirectory': privateDirectories,
                   'externalInterfaces': externalInterfaces,
                   'vlanInterfaces': vlanInterfaces}
        self.result = results
