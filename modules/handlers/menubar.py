from tkinter import Menu


def createMenubar(self):
    "Create our menu bar."

    font = self.font

    mbar = Menu(self.top, font=font)
    self.top.configure(menu=mbar)

    fileMenu = Menu(mbar, tearoff=False)
    mbar.add_cascade(label="File", font=font, menu=fileMenu)
    fileMenu.add_command(label="New", font=font, command=self.newTopology)
    fileMenu.add_command(label="Open", font=font,
                            command=self.loadTopology)
    fileMenu.add_command(label="Save", font=font,
                            command=self.saveTopology)
    fileMenu.add_command(label="Export Level 2 Script",
                            font=font, command=self.exportScript)
    fileMenu.add_command(label="Export LLM text tests",
                            font=font, command=self.llm_text_test_generation)
    fileMenu.add_command(label="Export LLM image tests",
                            font=font, command=self.llm_image_test_generation)
    fileMenu.add_separator()
    fileMenu.add_command(label='Quit', command=self.quit, font=font)

    editMenu = Menu(mbar, tearoff=False)
    mbar.add_cascade(label="Edit", font=font, menu=editMenu)
    editMenu.add_command(label="Cut", font=font,
                            command=lambda: self.deleteSelection(None))
    editMenu.add_command(label="Preferences", font=font,
                            command=self.prefDetails)

    runMenu = Menu(mbar, tearoff=False)
    mbar.add_cascade(label="Run", font=font, menu=runMenu)
    runMenu.add_command(label="Run", font=font, command=self.doRun)
    runMenu.add_command(label="Stop", font=font, command=self.doStop)
    fileMenu.add_separator()
    runMenu.add_command(label='Show OVS Summary',
                        font=font, command=self.ovsShow)
    runMenu.add_command(label='Root Terminal',
                        font=font, command=self.rootTerminal)

    # Application menu
    appMenu = Menu(mbar, tearoff=False)
    mbar.add_cascade(label="Help", font=font, menu=appMenu)
    appMenu.add_command(label='About MiniEdit', command=self.about,
                        font=font)

    