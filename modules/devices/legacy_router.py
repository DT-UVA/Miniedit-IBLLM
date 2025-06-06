from mininet.node import Node


class LegacyRouter(Node):
    "Simple IP router"

    def __init__(self, name, inNamespace=True, **params):
        Node.__init__(self, name, inNamespace, **params)

    # pylint: disable=arguments-differ
    def config(self, **_params):
        if self.intfs:
            self.setParam(_params, 'setIP', ip='0.0.0.0')
        r = Node.config(self, **_params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        return r