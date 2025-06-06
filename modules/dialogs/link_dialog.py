from tkinter import (Label, Entry, StringVar, E, W)
from tkinter import simpledialog as tkSimpleDialog


class LinkDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, title, linkDefaults):

        self.linkValues = linkDefaults

        tkSimpleDialog.Dialog.__init__(self, parent, title)

    def body(self, master):

        self.var = StringVar(master)
        Label(master, text="Bandwidth:").grid(row=0, sticky=E)
        self.e1 = Entry(master)
        self.e1.grid(row=0, column=1)
        Label(master, text="Mbit").grid(row=0, column=2, sticky=W)
        if 'bw' in self.linkValues:
            self.e1.insert(0, str(self.linkValues['bw']))

        Label(master, text="Delay:").grid(row=1, sticky=E)
        self.e2 = Entry(master)
        self.e2.grid(row=1, column=1)
        if 'delay' in self.linkValues:
            self.e2.insert(0, self.linkValues['delay'])

        Label(master, text="Loss:").grid(row=2, sticky=E)
        self.e3 = Entry(master)
        self.e3.grid(row=2, column=1)
        Label(master, text="%").grid(row=2, column=2, sticky=W)
        if 'loss' in self.linkValues:
            self.e3.insert(0, str(self.linkValues['loss']))

        Label(master, text="Max Queue size:").grid(row=3, sticky=E)
        self.e4 = Entry(master)
        self.e4.grid(row=3, column=1)
        if 'max_queue_size' in self.linkValues:
            self.e4.insert(0, str(self.linkValues['max_queue_size']))

        Label(master, text="Jitter:").grid(row=4, sticky=E)
        self.e5 = Entry(master)
        self.e5.grid(row=4, column=1)
        if 'jitter' in self.linkValues:
            self.e5.insert(0, self.linkValues['jitter'])

        Label(master, text="Speedup:").grid(row=5, sticky=E)
        self.e6 = Entry(master)
        self.e6.grid(row=5, column=1)
        if 'speedup' in self.linkValues:
            self.e6.insert(0, str(self.linkValues['speedup']))

        return self.e1  # initial focus

    def apply(self):
        self.result = {}
        if len(self.e1.get()) > 0:
            self.result['bw'] = int(self.e1.get())
        if len(self.e2.get()) > 0:
            self.result['delay'] = self.e2.get()
        if len(self.e3.get()) > 0:
            self.result['loss'] = int(self.e3.get())
        if len(self.e4.get()) > 0:
            self.result['max_queue_size'] = int(self.e4.get())
        if len(self.e5.get()) > 0:
            self.result['jitter'] = self.e5.get()
        if len(self.e6.get()) > 0:
            self.result['speedup'] = int(self.e6.get())