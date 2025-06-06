from mininet.node import UserSwitch


class CustomUserSwitch(UserSwitch):
    "Customized UserSwitch"

    def __init__(self, name, dpopts='--no-slicing', **kwargs):
        UserSwitch.__init__(self, name, **kwargs)
        self.switchIP = None

    def getSwitchIP(self):
        "Return management IP address"
        return self.switchIP

    def setSwitchIP(self, ip):
        "Set management IP address"
        self.switchIP = ip

    def start(self, controllers):
        "Start and set management IP address"
        # Call superclass constructor
        UserSwitch.start(self, controllers)
        # Set Switch IP address
        if self.switchIP is not None:
            if not self.inNamespace:
                self.cmd('ifconfig', self, self.switchIP)
            else:
                self.cmd('ifconfig lo', self.switchIP)