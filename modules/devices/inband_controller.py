from mininet.node import RemoteController


class InbandController(RemoteController):
    "RemoteController that ignores checkListening"

    def checkListening(self):
        "Overridden to do nothing."
        return