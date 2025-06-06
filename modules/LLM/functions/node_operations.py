from modules.LLM.constants import NODE_TYPES


def add_node_LLM(self, type: str, hostname: str, x: int, y: int) -> str:
    """
    Adds a node to the network

    :param name: (str) options are 'Host', 'Switch', 'LegacySwitch', 'LegacyRouter', 'Controller'
    :param x: (int) x coordinate
    :param y: (int) y coordinate
    :return: (str) node name
    """
    # Create a object with x and y coordinates
    coords = coordinateObject(x, y)

    # Create a new node
    if type in NODE_TYPES:
        # Create a new node with the given type and coordinates
        self.newNode(type, coords, hostname)

        # If the node is a host, return the last element of the hostOpts
        if type == 'Host':
            # Get the last element of the hostOpts
            return False, "Added: " + str(list(self.hostOpts)[-1])

        # If the node is a switch, return the last element of the switchOpts
        elif type == 'Controller':
            return False, "Added: " + str(list(self.controllers)[-1])
        
        # In all other cases, return the last element of the switchOpts
        else:
            return False, "Added: " + str(list(self.switchOpts)[-1])

    return True, 'Invalid node type'


def update_host_settings_LLM(self, name, ip, default_route):
    """
    Update the settings of a host in the network.

    :param name: (str) name of the host
    :param ip: (str) new IP address
    :param default_route: (str) new default route
    :return: (str) success message
    """
    if name not in self.hostOpts:
        return True, "Host not found"

    # Update the host's settings
    self.hostOpts[name]['ip'] = ip
    self.hostOpts[name]['defaultRoute'] = default_route

    # Notify the LLM
    return False, "Host settings updated successfully"


def update_node_location_LLM(self, name, new_x, new_y):
    """
    Update the location of a node in the network.

    :param name: (str) name of the node
    :param new_x: (int) new x coordinate
    :param new_y: (int) new y coordinate
    :return: (str) success message
    """
    # Get the node by name
    node = self.find_widget_by_name(name)

    # Check if the item is found
    if node is None:
        return True, "Node not found"
    
    # Update the node's position
    self.canvas.coords(node, new_x, new_y)

    # Get the widget
    node = self.itemToWidget[node]

    # Update all links connected to the node
    for widget, values in self.links.items():
        if values['src'] == node or values['dest'] == node:
            # Get the source and destination coordinates
            src_x, src_y = self.canvas.coords(self.widgetToItem[values['src']])
            dest_x, dest_y = self.canvas.coords(self.widgetToItem[values['dest']])

            # Update the link coordinates
            self.canvas.coords(widget, src_x, src_y, dest_x, dest_y)

    # Update scroll region
    self.updateScrollRegion()

    # Notify the LLM
    return False, "Node location updated successfully"
    

def delete_node_LLM(self, name):
    """
    Delete a node from the network.

    :param name: (str) name of the node
    :return: (str) success message
    """
    # Get the node by name
    node = self.find_widget_by_name(name)

    # Check if the item is found
    if node is None:
        return True, "Node not found"

    # Delete the node
    self.deleteNode(node)

    # Delete the item from the canvas
    self.canvas.delete(node)

    return False, "Node deleted successfully"


class coordinateObject(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y