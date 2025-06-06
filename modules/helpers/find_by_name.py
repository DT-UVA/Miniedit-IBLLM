

def find_widget_by_name(self, name):
    """
    Get the item associated with a given name.
    :param name: (str) name of the item
    :return: (str) item associated with the name
    """
    for item in self.itemToWidget:
        if self.itemToWidget[item].cget('text') == name:
            return item
    return None