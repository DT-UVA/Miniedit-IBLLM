FUNCTIONS = [
    {
        'type': 'function',
        'function': {
            'name': 'get_context',
            'description': '''
                Returns the current context of the network, including nodes and links. This is useful for understanding the current
                state of the network before making any changes. It also includes the coordinates of each node, which is important for
                graphical representation in the Miniedit GUI and settings of nodes/links such as IP addresses and default routes.''',
            'parameters': {},
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'add_node_LLM',
            'description': '''
                Adds a node to the network, where type can be Host, Switch, LegacySwitch, LegacyRouter, or Controller. An
                example of a call would be: add_node_LLM(Host, H1, 500, 371). The name of a node must follow the naming convention:
                H1, H2 for hosts, S1, S2 for switches, LS1, LS2 for legacy switches R1, R2 for legacy routers, and C1, C2 for controllers.
                The name of the node is optional. If not provided, a default name will be generated. The function will return the name of the node that was added.
                The X and Y coordinates have a min of X: 150, Y: 192 and a max of X: 1000, Y: 550. This said, the nodes should be placed in the center both 
                horizontally and vertically (around X:582, Y:399). When you add multiple nodes, please make sure that they are not overlapping. Do this by 
                having a difference of 80 on the same X or when you start a new row, have a difference of 80 on the Y axis.''',
            'parameters': {
                    'type': 'object',
                    'properties': {
                        'type': {
                            'type': 'string',
                            'description': "The type of node to add. Can be one of the following: Host, Switch, LegacySwitch, LegacyRouter, Controller."
                        },
                        'hostname': {
                            'type': 'string',
                            'description': "The name of the node to add."
                        },
                        'x': {
                            'type': 'integer',
                            'description': "The x-coordinate of the node. Must be between 150 and 1000."
                        },
                        'y': {
                            'type': 'integer',
                            'description': "The y-coordinate of the node. Must be between 192 and 550."
                        },
                    },
                'required': ['type', 'hostname', 'x', 'y'],
            },
        },
    },

    {
        'type': 'function',
        'function': {
            'name': 'delete_node_LLM',
            'description': '''
                Deletes a node from the network. An example of a call would be: delete_node_LLM(H1). This function should
                be used with caution, as it will remove the node and all links associated with it.''',
            'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': "The name of the node to delete. (e.g., H1, S1, LS1, R1, C1)."
                        },
                    },
                'required': ['name'],
            },
        },
    },

    {
        'type': 'function',
        'function': {
            'name': 'update_node_location_LLM',
            'description': '''Updates the (graphical) location of a node in Miniedit GUI. An example of a call would be: 
                update_node_location_LLM('H1', 500, 300). Links are automatically updated to reflect the new location of the node.
                The X and Y coordinates have a min of X: 150, Y: 192 and a max of X: 1000, Y: 550. This said, the nodes should be 
                placed in the center both horizontally and vertically (around X:582, Y:399). When you add multiple nodes, please 
                make sure that they are not overlapping. Do this by having a difference of 80 on the same X  or when you start a
                new row, have a difference of 80 on the Y axis.''',
            'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': "The name of the node to update."
                        },
                        'new_x': {
                            'type': 'integer',
                            'description': "The new x-coordinate of the node. Must be between 150 and 1000."
                        },
                        'new_y': {
                            'type': 'integer',
                            'description': "The new y-coordinate of the node. Must be between 192 and 550."
                        },
                    },
                'required': ['name', 'new_x', 'new_y'],
            },
        },
    },

    {
        'type': 'function',
        'function': {
            'name': 'update_host_settings_LLM',
            'description': '''Updates the settings of a host in the network. An example of a call would be: 
                            update_host_settings_LLM('H1', '10.0.0.10', '10.0.0.1/24'), when multiple nodes need to communicate with each other,
                            you need to update the settings of each host. The IP address and default route are important for the network to function correctly.''',
            'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': "The name of the node to update."
                        },
                        'ip': {
                            'type': 'string',
                            'description': "The new IP address of the node. An example would be 10.0.0.1"
                        },
                        'default_route': {
                            'type': 'string',
                            'description': "The new default route of the node. An example would be 10.0.0.1/24"
                        },
                    },
                'required': ['name', 'ip', 'default_route'],
            },
        },
    },

    {
        'type': 'function',
        'function': {
            'name': 'add_link_LLM',
            'description': '''Adds a link between two nodes in the network. An example of a call would be: add_link_LLM('H1', 'S1'). This connects them on a network level.
              Connections between hosts-hosts are not allowed, FOR THIS YOU NEED TO ADD A INTERMEDIATE NODE (SWITCH OR ROUTER).''',
            'parameters': {
                    'type': 'object',
                    'properties': {
                        'source': {
                            'type': 'string',
                            'description': "The name of the first node to link."
                        },
                        'destination': {
                            'type': 'string',
                            'description': "The name of the second node to link."
                        },
                    },
                'required': ['source', 'destination'],
            },
        },
    },

    {
        'type': 'function',
        'function': {
            'name': 'update_link_settings_LLM',
            'description': '''Updates/changes the settings of a link between two nodes in the network. An example of a call would be: 
                update_link_settings_LLM('H1', 'S1', 1000, 10, 0, 0, 0, 0, 1). Only update the settings which are asked for in the prompt. 
                You can update the following settings: bandwidth, delay, loss, max_queue_size, jitter, speedup.''',
            'parameters': {
                    'type': 'object',
                    'properties': {
                        'source': {
                            'type': 'string',
                            'description': "The name of the first node to link."
                        },
                        'destination': {
                            'type': 'string',
                            'description': "The name of the second node to link."
                        },
                        'bandwidth': {
                            'type': 'integer',
                            'description': "The bandwidth of the link."
                        },
                        'delay': {
                            'type': 'integer',
                            'description': "The delay of the link."
                        },
                        'loss': {
                            'type': 'integer',
                            'description': "The loss of the link."
                        },
                        'max_queue_size': {
                            'type': 'integer',
                            'description': "The maximum queue size of the link."
                        },
                        'jitter': {
                            'type': 'integer',
                            'description': "The jitter of the link."
                        },
                        'speedup': {
                            'type': 'integer',
                            'description': "The speedup of the link."
                        },
                    },
            },
        },
    },

    {
        'type': 'function',
        'function': {
            'name': 'remove_link_LLM',
            'description': '''Removes a link/connection between two nodes in the network. An example of a call would be: remove_link_LLM('H1', 'S1').''',
            'parameters': {
                    'type': 'object',
                    'properties': {
                        'source': {
                            'type': 'string',
                            'description': "The name of the first node to link."
                        },
                        'destination': {
                            'type': 'string',
                            'description': "The name of the second node to link."
                        },
                    },
                'required': ['source', 'destination'],
            },
        },
    },
]
