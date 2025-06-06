def get_context(self) -> dict:
    """
    Get the context of the network.

    Contains:
    - nodes: list of nodes in the network
    - links: list of nodes in the network [(source, destination), ...]
    :return: (dict) dictionary containing the details of the network
    """
    context = {
        'nodes': self.get_nodes(),
        'links': self.get_links(),
    }
    return False, context


def get_nodes(self) -> list:
    """
    List all existing nodes in the network.
    
    :return: (list) list of node names containing the details and coordinates
    """
    nodes = []

    # Parse switches and routers
    for key, value in self.switchOpts.items():
        # Get the coordinates of the node
        x, y = self.get_coordinates(key)
        if x is None: continue
        nodes.append((value, {'x': x, 'y': y}))

    # Parse hosts
    for key, value in self.hostOpts.items():
        # Get the coordinates of the node
        x, y = self.get_coordinates(key)
        if x is None: continue
        nodes.append((value, {'x': x, 'y': y}))

    # Parse controllers
    for key, value in self.controllers.items():
        # Get the coordinates of the node
        x, y = self.get_coordinates(key)
        if x is None: continue
        nodes.append((value, {'x': x, 'y': y}))

    # Return the list of nodes
    return nodes


def get_links(self) -> list:
    """
    Get the links between nodes.

    :return: (list) list of links containing the details and coordinates
    """
    links = []

    # Parse links
    for key, value in self.links.items():
        src = value['src'].cget('text')
        dest = value['dest'].cget('text')
        links.append({(src, dest): {'link_options': value['linkOpts']}})

    # Return the list of links
    return links


def get_coordinates(self, key):
    """
    Get the coordinates of a node.

    :param key: (str) name of the node
    :return: (tuple) coordinates of the node
    """
    # Check if the key is in the itemToWidget dictionary
    for i in self.itemToWidget:
        if self.itemToWidget[i].cget('text') == key:
            return self.itemToWidget[i].winfo_rootx(), self.itemToWidget[i].winfo_rooty()
    return None, None

