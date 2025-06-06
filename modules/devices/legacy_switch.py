from mininet.node import OVSSwitch

class LegacySwitch(OVSSwitch):
    "OVS switch in standalone/bridge mode"

    def __init__(self, name, **params):
        OVSSwitch.__init__(self, name, failMode='standalone', **params)
        self.switchIP = None