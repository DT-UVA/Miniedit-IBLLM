from ollama import ChatResponse, chat

from modules.LLM.constants import *
from modules.LLM.functions.multimodal_layer import analyse_image
from modules.LLM.tools import FUNCTIONS

def LLMChat(self):
    """
    This function is used to chat with the LLM. It takes the text input (possibly an image as well) from the 
    user and sends it to the LLM. The LLM will then respond with the actions to be taken.

    :param self: The class instance
    :param text: The text input from the user
    :return: A dictionary containing the actions and responses from the LLM
    """
    # Set the actions and responses dictionary
    actions_and_responses = {
        'input': self.chat_history[-1]['content'],
        'tool_calls': [],
        'initial_response': None,
        'final_response': None
    }

    if len(self.imageUploaded) > 0:
        # Inform the user that the LLM is analyzing the image
        self.update_state_button('Analyzing the image...')

        # Get the image information
        self.imageUploaded = analyse_image(self.imageUploaded)

        # Pop the last message from the chat history
        prompt = self.chat_history.pop()

        self.chat_history.extend([
            {'role': 'user', 'content': 'Given this image description: ' + str(self.imageUploaded) + ' do the following: ' + prompt['content']},
        ])

    # Add the response message to the messages list
    available_functions = {
        # get context
        'get_context': self.get_context, 

        # node operations
        'add_node_LLM': self.add_node_LLM, 
        'delete_node_LLM': self.delete_node_LLM,
        'update_node_location_LLM': self.update_node_location_LLM,
        'update_host_settings_LLM': self.update_host_settings_LLM,

        # link operations
        'add_link_LLM': self.add_link_LLM, 
        'remove_link_LLM': self.remove_link_LLM, 
        'update_link_settings_LLM': self.update_link_settings_LLM,
    }


    # Go through the tool calls
    function_execution(self, available_functions, actions_and_responses)

    # Generate the final response
    final_response(self, actions_and_responses)

    # Add the final response to the chat history
    self.chat_history.extend([
        {'role': 'assistant', 'content': actions_and_responses['final_response']},
    ])

    return actions_and_responses


def function_execution(self, available_functions: list, actions_and_responses: dict):
    """
    This function is used to execute the functions called by the LLM. It takes the response from the LLM and executes 
    the functions called by the LLM. Through iteration, it will call the functions until there are no more tool calls 
    and correct the errors.
    
    :param self: The class instance
    :param response: The response from the LLM
    :param functions_json: The functions available to the LLM
    :param available_functions: The functions available to the LLM
    :param messages: The messages list
    :return: A list with the successful tool calls
    """
    # Failure counter to prevent bias problems
    failures, iterations = 0, 0

    # List to store the successful tool calls
    successfull_tool_calls = []

    # Inform the user that the LLM is thinking
    self.update_state_button('Thinking...') 

    # Add the user message to the messages list
    response: ChatResponse = chat(
        TEXT_MODEL,
        messages=self.chat_history,
        tools=FUNCTIONS,
        options={"temperature": TEMPERATURE}
    )

    # Let the user know that the LLM is executing the actions
    if response.message.tool_calls:
        self.update_state_button('Executing the tools...')
    else:
        actions_and_responses['initial_response'] = response.message.content
        return 
    
    while response.message.tool_calls or "[TOOL_CALLS]" in response.message.content or len(tool_calls['failed_tool_calls']) > 0:
        # Store the tool calls in a dictionary
        tool_calls = {'successfull_tool_calls': [], 'failed_tool_calls': []}

        # If there are no tool calls, we need to break the loop
        if response.message.tool_calls is None:
            break

        # There may be multiple tool calls in the response
        for tool in response.message.tool_calls:
            # Ensure the function is available, and then call it
            if function_to_call := available_functions.get(tool.function.name):
                try:
                    error, output = function_to_call(**tool.function.arguments)
                except Exception as e:
                    error = True
                    output = str(e)

                self.chat_history.extend([
                    {'role': 'tool', 'content': str(output), 'name': tool.function.name}
                ])
                
                # Handle errors and output
                if not error:
                    tool_calls['successfull_tool_calls'].append({
                        'function': tool.function.name,
                        'arguments': tool.function.arguments,
                        'output': str(output)})
                else:
                    tool_calls['failed_tool_calls'].append({
                        'function': tool.function.name,
                        'arguments': tool.function.arguments,
                        'output': str(output)})
                    
        # Store the tool calls in the actions and responses dictionary
        if len(tool_calls['successfull_tool_calls']) > 0:
            actions_and_responses['tool_calls'].extend(tool_calls['successfull_tool_calls'])


        # Construct the new prompt to correct errors or add more information
        delta = ""

        # Check for errors
        if len(tool_calls['failed_tool_calls']) > 0: 
            # Increment the failure counter
            failures += 1

            delta += f"There were some errors in the tool calls: {tool_calls['failed_tool_calls']}, correct them (only if the errors are something that needs to be corrected) and try again. \n"


        # Append the delta to the chat history
        if len(delta) > 0:
            self.chat_history.extend([
                {'role': 'user', 'content': delta},

        ])

        # If we have failed too many times, we need to break the loop
        if failures == MAX_FAILURES or iterations == MAX_ITERATIONS: 
            return successfull_tool_calls
            
        # Increase the iterations
        iterations += 1


        # Try again to get the final response
        response = chat(TEXT_MODEL, messages=self.chat_history, tools=FUNCTIONS, options={"temperature": TEMPERATURE})

    if actions_and_responses['initial_response'] is None:
        actions_and_responses['initial_response'] = response.message.content


def final_response(self, actions_and_responses: dict):
    """
    This function is used to get the final response from the LLM. It takes the actions and responses dictionary and
    generates the final response from the LLM. It will also add the final response to the actions and responses dictionary.

    :param self: The class instance
    :param actions_and_responses: The actions and responses dictionary
    :return: A dictionary with the actions and responses
    """

    # Construct a messages list
    messages = []

    if actions_and_responses['initial_response'] is None:
        messages.extend([
            {'role': 'system', 'content': FINAL_RESPONSE_PROMPT},
            {'role': 'user', 'content': 'This is what has been done so far, explain and summarize it: ' + str(actions_and_responses['tool_calls']) + ' and'
            '        ask what the user wants to do next. I want you to form it as if this information is new for me, and I am not aware of it. '},
        ])
    else:
        messages.extend([
            {'role': 'system', 'content': FINAL_RESPONSE_PROMPT},
            {'role': 'tool', 'content': str(actions_and_responses['tool_calls'])},
            {'role': 'user', 'content': str(actions_and_responses['initial_response'])},
        ])
    
    # Call the LLM to get the final response
    response = chat(FINAL_RESPONSE_MODEL, messages=messages)

    # Add the final response to the messages list
    add_chatmessage(self, response.message.content)

    # Add the final response to the messages list
    actions_and_responses['final_response'] = response.message.content

    # Return the submit button to its original state
    self.update_state_button('Submit prompt')


def add_chatmessage(self, message: str):
    """
    This function is used to add a chat message to the chat history. It takes the message and adds it to the chat history.

    :param self: The class instance
    :param message: The message to be added
    """
    # Get final response from model with function outputs
    self.chatHistory.config(state='normal')  # Enable editing temporarily
    self.chatHistory.insert("end", f"LLM: {message}\n")
    self.chatHistory.config(state='disabled')  # Make it read-only again
    self.chatHistory.see("end")  # Scroll to the bottom

    self.update()  # Update the GUI
    self.update_idletasks()  # Process any pending events


def update_state_button(self, state: str):
    """
    This function is used to update the state of the button. It is used to enable or disable the button based on the state of the chat.
    """
    # Enable or disable the button based on the state of the chat
    if state == "Submit prompt":
        self.submitButton.config(text=state)
        self.submitButton.config(state='normal')
    else:
        self.submitButton.config(text=state)
        self.submitButton.config(state='disabled')

    # Update the GUI
    self.update()
    self.update_idletasks()  

