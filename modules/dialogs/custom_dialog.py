from tkinter import Toplevel, Frame, Button, E, W


class CustomDialog(object):
    def __init__(self, master, _title):
        self.top = Toplevel(master)

        self.bodyFrame = Frame(self.top)
        self.bodyFrame.grid(row=0, column=0, sticky='nswe')
        self.body(self.bodyFrame)

        # return self.b # initial focus
        buttonFrame = Frame(self.top, relief='ridge', bd=3, bg='lightgrey')
        buttonFrame.grid(row=1, column=0, sticky='nswe')

        okButton = Button(buttonFrame, width=8, text='OK', relief='groove',
                          bd=4, command=self.okAction)
        okButton.grid(row=0, column=0, sticky=E)

        canlceButton = Button(buttonFrame, width=8, text='Cancel', relief='groove',
                              bd=4, command=self.cancelAction)
        canlceButton.grid(row=0, column=1, sticky=W)

    def body(self, master):
        self.rootFrame = master

    def apply(self):
        self.top.destroy()

    def cancelAction(self):
        self.top.destroy()

    def okAction(self):
        self.apply()
        self.top.destroy()