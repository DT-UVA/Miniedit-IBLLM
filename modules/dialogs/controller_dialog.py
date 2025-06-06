from tkinter import (Label, LabelFrame, Entry, OptionMenu, StringVar, E, W)
from tkinter import simpledialog as tkSimpleDialog

class ControllerDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, title, ctrlrDefaults=None):

        if ctrlrDefaults:
            self.ctrlrValues = ctrlrDefaults

        tkSimpleDialog.Dialog.__init__(self, parent, title)

    def body(self, master):

        self.var = StringVar(master)
        self.protcolvar = StringVar(master)

        rowCount = 0
        # Field for Hostname
        Label(master, text="Name:").grid(row=rowCount, sticky=E)
        self.hostnameEntry = Entry(master)
        self.hostnameEntry.grid(row=rowCount, column=1)
        self.hostnameEntry.insert(0, self.ctrlrValues['hostname'])
        rowCount += 1

        # Field for Remove Controller Port
        Label(master, text="Controller Port:").grid(row=rowCount, sticky=E)
        self.e2 = Entry(master)
        self.e2.grid(row=rowCount, column=1)
        self.e2.insert(0, self.ctrlrValues['remotePort'])
        rowCount += 1

        # Field for Controller Type
        Label(master, text="Controller Type:").grid(row=rowCount, sticky=E)
        controllerType = self.ctrlrValues['controllerType']
        self.o1 = OptionMenu(master, self.var, "Remote Controller",
                             "In-Band Controller", "OpenFlow Reference", "OVS Controller")
        self.o1.grid(row=rowCount, column=1, sticky=W)
        if controllerType == 'ref':
            self.var.set("OpenFlow Reference")
        elif controllerType == 'inband':
            self.var.set("In-Band Controller")
        elif controllerType == 'remote':
            self.var.set("Remote Controller")
        else:
            self.var.set("OVS Controller")
        rowCount += 1

        # Field for Controller Protcol
        Label(master, text="Protocol:").grid(row=rowCount, sticky=E)
        if 'controllerProtocol' in self.ctrlrValues:
            controllerProtocol = self.ctrlrValues['controllerProtocol']
        else:
            controllerProtocol = 'tcp'
        self.protcol = OptionMenu(master, self.protcolvar, "TCP", "SSL")
        self.protcol.grid(row=rowCount, column=1, sticky=W)
        if controllerProtocol == 'ssl':
            self.protcolvar.set("SSL")
        else:
            self.protcolvar.set("TCP")
        rowCount += 1

        # Field for Remove Controller IP
        remoteFrame = LabelFrame(
            master, text='Remote/In-Band Controller', padx=5, pady=5)
        remoteFrame.grid(row=rowCount, column=0, columnspan=2, sticky=W)

        Label(remoteFrame, text="IP Address:").grid(row=0, sticky=E)
        self.e1 = Entry(remoteFrame)
        self.e1.grid(row=0, column=1)
        self.e1.insert(0, self.ctrlrValues['remoteIP'])
        rowCount += 1

        return self.hostnameEntry  # initial focus

    def apply(self):
        self.result = {'hostname': self.hostnameEntry.get(),
                       'remoteIP': self.e1.get(),
                       'remotePort': int(self.e2.get())}

        controllerType = self.var.get()
        if controllerType == 'Remote Controller':
            self.result['controllerType'] = 'remote'
        elif controllerType == 'In-Band Controller':
            self.result['controllerType'] = 'inband'
        elif controllerType == 'OpenFlow Reference':
            self.result['controllerType'] = 'ref'
        else:
            self.result['controllerType'] = 'ovsc'
        controllerProtocol = self.protcolvar.get()
        if controllerProtocol == 'SSL':
            self.result['controllerProtocol'] = 'ssl'
        else:
            self.result['controllerProtocol'] = 'tcp'