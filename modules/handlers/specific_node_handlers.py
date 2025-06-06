from tkinter import (Label, Entry, Toplevel, Wm, CENTER)

from modules.miniedit_utils.definitions import MINIEDIT_VERSION


def selectNode(self, event):
    "Select the node that was clicked on."
    item = self.widgetToItem.get(event.widget, None)
    self.selectItem(item)

def dragNodeAround(self, event):
    "Drag a node around on the canvas."
    c = self.canvas
    # Convert global to local coordinates;
    # Necessary since x, y are widget-relative
    x = self.canvasx(event.x_root)
    y = self.canvasy(event.y_root)
    w = event.widget
    # Adjust node position
    item = self.widgetToItem[w]
    c.coords(item, x, y)
    # Adjust link positions
    for dest in w.links:
        link = w.links[dest]
        item = self.widgetToItem[dest]
        x1, y1 = c.coords(item)
        c.coords(link, x, y, x1, y1)
        
    self.updateScrollRegion()

def createControlLinkBindings(self):
    "Create a set of bindings for nodes."
    # Link bindings
    # Selection still needs a bit of work overall
    # Callbacks ignore event

    def select(_event, link=self.link):
        "Select item on mouse entry."
        self.selectItem(link)

    def highlight(_event, link=self.link):
        "Highlight item on mouse entry."
        self.selectItem(link)
        self.canvas.itemconfig(link, fill='green')

    def unhighlight(_event, link=self.link):
        "Unhighlight item on mouse exit."
        self.canvas.itemconfig(link, fill='red')
        # self.selectItem( None )

    self.canvas.tag_bind(self.link, '<Enter>', highlight)
    self.canvas.tag_bind(self.link, '<Leave>', unhighlight)
    self.canvas.tag_bind(self.link, '<ButtonPress-1>', select)

def createDataLinkBindings(self):
    "Create a set of bindings for nodes."
    # Link bindings
    # Selection still needs a bit of work overall
    # Callbacks ignore event

    def select(_event, link=self.link):
        "Select item on mouse entry."
        self.selectItem(link)

    def highlight(_event, link=self.link):
        "Highlight item on mouse entry."
        self.selectItem(link)
        self.canvas.itemconfig(link, fill='green')

    def unhighlight(_event, link=self.link):
        "Unhighlight item on mouse exit."
        self.canvas.itemconfig(link, fill='blue')
        # self.selectItem( None )

    self.canvas.tag_bind(self.link, '<Enter>', highlight)
    self.canvas.tag_bind(self.link, '<Leave>', unhighlight)
    self.canvas.tag_bind(self.link, '<ButtonPress-1>', select)
    self.canvas.tag_bind(self.link, '<Button-3>', self.do_linkPopup)

def startLink(self, event):
    "Start a new link."
    if event.widget not in self.widgetToItem:
        # Didn't click on a node
        return

    w = event.widget
    item = self.widgetToItem[w]
    x, y = self.canvas.coords(item)
    self.link = self.canvas.create_line(x, y, x, y, width=4,
                                        fill='blue', tag='link')
    self.linkx, self.linky = x, y
    self.linkWidget = w
    self.linkItem = item

def finishLink(self, event):
    "Finish creating a link"
    if self.link is None:
        return
    source = self.linkWidget
    c = self.canvas
    
    # Since we dragged from the widget, use root coords
    x, y = self.canvasx(event.x_root), self.canvasy(event.y_root)
    target = self.findItem(x, y)
    dest = self.itemToWidget.get(target, None)
    if (source is None or dest is None or source == dest
            or dest in source.links or source in dest.links):
        self.releaseNetLink(event)
        return
    
    # For now, don't allow hosts to be directly linked
    stags = self.canvas.gettags(self.widgetToItem[source])
    dtags = self.canvas.gettags(target)

    # pylint: disable=too-many-boolean-expressions
    if (('Host' in stags and 'Host' in dtags) or
        ('Controller' in dtags and 'LegacyRouter' in stags) or
        ('Controller' in stags and 'LegacyRouter' in dtags) or
        ('Controller' in dtags and 'LegacySwitch' in stags) or
        ('Controller' in stags and 'LegacySwitch' in dtags) or
        ('Controller' in dtags and 'Host' in stags) or
        ('Controller' in stags and 'Host' in dtags) or
        ('Controller' in stags and 'Controller' in dtags)):
        self.releaseNetLink(event)
        return

    # Set link type
    linkType = 'data'
    if 'Controller' in stags or 'Controller' in dtags:
        linkType = 'control'
        c.itemconfig(self.link, dash=(6, 4, 2, 4), fill='red')
        self.createControlLinkBindings()
    else:
        linkType = 'data'
        self.createDataLinkBindings()
    c.itemconfig(self.link, tags=c.gettags(self.link)+(linkType,))

    x, y = c.coords(target)
    c.coords(self.link, self.linkx, self.linky, x, y)
    self.addLink(source, dest, linktype=linkType)
    if linkType == 'control':
        controllerName = ''
        switchName = ''
        if 'Controller' in stags:
            controllerName = source['text']
            switchName = dest['text']
        else:
            controllerName = dest['text']
            switchName = source['text']

        self.switchOpts[switchName]['controllers'].append(controllerName)

    # We're done
    self.link = self.linkWidget = None

def about(self):
    "Display about box."
    about = self.aboutBox
    if about is None:
        bg = 'white'
        about = Toplevel(bg='white')
        about.title('About')
        desc = self.appName + ': a simple network editor for MiniNet'
        version = 'MiniEdit '+ MINIEDIT_VERSION
        author = 'Originally by: Bob Lantz <rlantz@cs>, April 2010, Enhancements by: Gregory Gee, Since July 2013'
        enhancements = 'LLM-IBN integration by: Dani Termaat, May 2025'
        www = 'http://gregorygee.wordpress.com/category/miniedit/'
        line1 = Label(about, text=desc, font='Helvetica 10 bold', bg=bg)
        line2 = Label(about, text=version, font='Helvetica 9', bg=bg)
        line3 = Label(about, text=author, font='Helvetica 9', bg=bg)
        line4 = Label(about, text=enhancements, font='Helvetica 9', bg=bg)
        line5 = Entry(about, font='Helvetica 9', bg=bg,
                        width=len(www), justify=CENTER)
        line5.insert(0, www)
        line5.configure(state='readonly')
        line1.pack(padx=20, pady=10)
        line2.pack(pady=10)
        line3.pack(pady=10)
        line4.pack(pady=10)
        line5.pack(pady=10)

        def hide():
            about.withdraw()
        self.aboutBox = about
        # Hide on close rather than destroying window
        Wm.wm_protocol(about, name='WM_DELETE_WINDOW', func=hide)
    # Show (existing) window
    about.deiconify()

def createToolImages(self):
    "Create toolbar (and icon) images."
