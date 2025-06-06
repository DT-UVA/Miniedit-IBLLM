def do_linkPopup(self, event):
    # display the popup menu
    if self.net is None:
        try:
            self.linkPopup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.linkPopup.grab_release()
    else:
        try:
            self.linkRunPopup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.linkRunPopup.grab_release()

def do_controllerPopup(self, event):
    # display the popup menu
    if self.net is None:
        try:
            self.controllerPopup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.controllerPopup.grab_release()

def do_legacyRouterPopup(self, event):
    # display the popup menu
    if self.net is not None:
        try:
            self.legacyRouterRunPopup.tk_popup(
                event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.legacyRouterRunPopup.grab_release()

def do_hostPopup(self, event):
    # display the popup menu
    if self.net is None:
        try:
            self.hostPopup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.hostPopup.grab_release()
    else:
        try:
            self.hostRunPopup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.hostRunPopup.grab_release()

def do_legacySwitchPopup(self, event):
    # display the popup menu
    if self.net is not None:
        try:
            self.switchRunPopup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.switchRunPopup.grab_release()

def do_switchPopup(self, event):
    # display the popup menu
    if self.net is None:
        try:
            self.switchPopup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.switchPopup.grab_release()
    else:
        try:
            self.switchRunPopup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.switchRunPopup.grab_release()