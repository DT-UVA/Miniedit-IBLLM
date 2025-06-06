from mininet.node import OVSSwitch


class customOvs(OVSSwitch):
    "Customized OVS switch"

    def __init__(self, name, failMode='secure', datapath='kernel', **params):
        OVSSwitch.__init__(self, name, failMode=failMode,
                           datapath=datapath, **params)
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
        OVSSwitch.start(self, controllers)
        # Set Switch IP address
        if self.switchIP is not None:
            self.cmd('ifconfig', self, self.switchIP)