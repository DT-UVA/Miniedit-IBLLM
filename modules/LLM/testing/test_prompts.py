#### TOOL TEXT USAGE TESTS ####
TOOL_USAGE_TESTS = {
    "TUT_1": "Add a host to the middle of the network. Update the host its settings its settings to IP: 10.0.0.10 and default route: 10.0.0.1/24",
    "TUT_2": "Add two hosts and connect them to a switch. Configure the hosts in the network to an IP address in the 10.0.0.1/24 subnet.",
    "TUT_3": "Add two hosts, a switch and controller to the network. Add a link between the hosts to the switch and the switch to the controller. After, update the links their bandwidth between the switch and hosts to 1000 Mbps.",
    "TUT_4": "Add a host to X:80, Y:80. After, change the host's location to X:200, Y:200.",
    "TUT_5": "Add three hosts, a switch and a controller to the network. Connect the hosts to the switch and the switch to the controller. After, delete one of the links between the switch and controller.",
    "TUT_6": "Add three hosts to the network. After, delete one of the host.",
}

# ALL TEXT TESTS
LLM_TEXT_TESTS_GENERATION = {"test_text_tool_usage": TOOL_USAGE_TESTS}


# ALL IMAGE TESTS (EMPTY FOR NOW)
LLM_IMAGE_TESTS_GENERATION = {}