def add_link_LLM(self, source, destination):
    """
    Add a link between two nodes in the network.

    :param source: (str) name of the first node
    :param destination: (str) name of the second node
    :return: (str) confirmation message
    """
    # Find the widget for the first node
    item1 = self.find_widget_by_name(source)
    item2 = self.find_widget_by_name(destination)

    # Feedback for the LLM
    if item1 is None:
        return True, "Node {} not found.".format(source)
    if item2 is None:
        return True, "Node {} not found.".format(destination)
    
    # Get the widgets for the nodes
    node1_widget = self.itemToWidget[item1]
    node2_widget = self.itemToWidget[item2]

    # Check if the link already exists
    for key, link in self.links.items():
        if (link['src'] == node1_widget and link['dest'] == node2_widget) or \
              (link['src'] == node2_widget and link['dest'] == node1_widget):
            return True, "Link already exists between {} and {}.".format(source, destination)
        
    # Check if both nodes are found
    if node1_widget is None or node2_widget is None:
        return "One or both nodes not found."

    item = self.widgetToItem[node1_widget]
    x, y = self.canvas.coords(item)

    self.link = self.canvas.create_line(x, y, x, y, width=4, fill='blue', tag='link')
    self.linkx, self.linky = x, y
    self.linkWidget = node1_widget
    self.linkItem = item

    "Finish creating a link"
    src = self.linkWidget
    c = self.canvas
    
    target = self.widgetToItem.get(node2_widget, None)
    dest = self.itemToWidget.get(target, None)

    if (src is None or dest is None or src == dest):
        return "Invalid link configuration."
    
    # For now, don't allow hosts to be directly linked
    stags = self.canvas.gettags(self.widgetToItem[src])
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
        return True, "Invalid link configuration. Cannot link two hosts or a host to a controller. Add intermediate switches or routers."

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
    self.addLink(src, dest, linktype=linkType)
    if linkType == 'control':
        controllerName = ''
        switchName = ''
        if 'Controller' in stags:
            controllerName = src['text']
            switchName = dest['text']
        else:
            controllerName = dest['text']
            switchName = src['text']

        self.switchOpts[switchName]['controllers'].append(controllerName)

    self.link = None
    self.linkWidget = None
    self.link = self.linkWidget = None

    return False, "Link added between {} and {}.".format(source, destination)


def update_link_settings_LLM(self, source, destination, bandwidth=0, delay=0, loss=0, max_queue_size=0, jitter=0, speedup=0):
    """
    Update the settings of a link between two nodes in the network.

    :param source: (str) name of the first node
    :param node2: (str) name of the second node
    :param bandwidth: (int) bandwidth of the link
    :param delay: (int) delay of the link
    :param loss: (int %) loss of the link
    :param max_queue_size: (int) maximum queue size of the link
    :param jitter: (int) jitter of the link
    :param speedup: (int) speedup of the link
    :return: (str) confirmation message
    """
    # Find the widget for the first node
    item1 = self.find_widget_by_name(source)
    item2 = self.find_widget_by_name(destination)

    # Feedback for the LLM
    if item1 is None:
        return True, "Node {} not found.".format(source)
    if item2 is None:
        return True, "Node {} not found.".format(destination)
    
    # Get the widgets for the nodes
    node1_widget = self.itemToWidget[item1]
    node2_widget = self.itemToWidget[item2]

    # Find the link between the two nodes
    for key, link in self.links.items():
        if (link['src'] == node1_widget and link['dest'] == node2_widget) or \
              (link['src'] == node2_widget and link['dest'] == node1_widget):
            linkOpts = {
                'bw': int(bandwidth),
                'delay': int(delay),
                'loss': int(loss),
                'max_queue_size': int(max_queue_size),
                'jitter': int(jitter),
                'speedup': int(speedup)
            }

            # Update the link settings
            self.links[key]['linkOpts'].update(linkOpts)

    return False, "Link settings updated between {} and {}.".format(source, destination)


def remove_link_LLM(self, source, destination):
    """
    Remove a link between two nodes in the network.
    
    :param node1: (str) name of the first node
    :param node2: (str) name of the second node
    :return: (str) confirmation message
    """
    # Find the widget for the first node
    item1 = self.find_widget_by_name(source)
    item2 = self.find_widget_by_name(destination)

    # Feedback for the LLM
    if item1 is None:
        return True, "Node {} not found.".format(source)
    if item2 is None:
        return True, "Node {} not found.".format(destination)
    
    # Get the widgets for the nodes
    node1_widget = self.itemToWidget[item1]
    node2_widget = self.itemToWidget[item2]

    # Find the link between the two nodes
    for key, link in self.links.items():
        if (link['src'] == node1_widget and link['dest'] == node2_widget) or \
              (link['src'] == node2_widget and link['dest'] == node1_widget):
            # Remove the link
            self.deleteLink(key)

            # Remove the link from the canvas
            self.canvas.delete(key)

            # Return a confirmation message
            return False, "Link removed between {} and {}.".format(source, destination)
        
    # If no link was found, return a message
    return True, "No link found between {} and {}.".format(source, destination)