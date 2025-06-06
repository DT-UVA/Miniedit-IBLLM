import json
import os
import base64

from modules.LLM.testing.test_prompts import *
from modules.LLM.constants import LLM_TOOLS_TEXT_PROMPT


def llm_text_test_generation(self):
    """
    Run the LLM tests for generation and save the results to a file.
    This function will iterate through the test prompts defined in
    LLM_TESTS_GENERATION, execute them, and save the results in a JSON file.

    The results will be saved in a test_results in the
    current working directory. The file will contain a list of dictionaries,
    each containing the test name and the corresponding output from the LLM.
    """

    # Add the test results directory if it doesn't exist
    if not os.path.exists('test_results'):
        os.makedirs('test_results')

    # Go through the tests
    for setname, tests in LLM_TEXT_TESTS_GENERATION.items():
        # Place to store the results
        test_results = []

        # Iterate through the test prompts
        for test_name, test_prompt in tests.items():
            self.newTopology()
            self.chat_history.clear()
            self.chat_history.extend([
                # Add the system prompt to the chat history
                {'role': 'system', 'content': LLM_TOOLS_TEXT_PROMPT},
                {'role': 'user', 'content': test_prompt},
            ])
            output = self.LLMChat()

            # Append the result to the results list 
            test_results.append({'test_name': test_name, 'result': output})

        # Save the test results to a file
        with open(f'test_results/{setname}.json', 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=4)

    # Clear the chat history
    self.chatHistory.config(state='normal')  # Enable editing temporarily
    self.chatHistory.delete(1.0, "end")  # Clear the chat history
    self.chatHistory.see("end")  # Scroll to the bottom
    self.chatHistory.insert("end", f"Finished testing, results saved to test_results.json\n")
    self.chatHistory.config(state='disabled')  # Make it read-only again


def llm_image_test_generation(self):
    """
    Run the LLM tests for image generation and save the results to a file.
    This function will iterate through the test prompts defined in
    LLM_IMAGE_TESTS_GENERATION, execute them, and save the results in a JSON file.
    The results will be saved in a test_results in the current working directory. 
    The file will contain a list of dictionaries, each containing the test name
      and the corresponding output from the LLM.
    """
    # Add the test results directory if it doesn't exist
    if not os.path.exists('test_results'):
        os.makedirs('test_results')

    # Go through the tests
    for setname, tests in LLM_IMAGE_TESTS_GENERATION.items():
        # Place to store the results
        test_results = []

        # Iterate through the test prompts
        for test_name, values in tests.items():
            # Check if the image file exists
            image_path = values['image']

            # Check if the image file exists
            if not os.path.exists(image_path):
                continue

            # Check if the file is an image
            if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                continue 

            # Get the image
            with open(image_path, 'rb') as image_file:
                # Read the image file
                image_data = image_file.read()
                # Convert the image data to a base64 string
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                # Store the base64 string in the instance variable
                self.imageUploaded = image_base64


            self.newTopology()
            self.chat_history.clear()
            self.chat_history.extend([
                # Add the system prompt to the chat history
                {'role': 'system', 'content': LLM_TOOLS_TEXT_PROMPT},
                {'role': 'user', 'content': values['prompt']},
            ])
            output = self.LLMChat()

            # Append the result to the results list 
            test_results.append({'test_name': test_name, 'result': output})

            # Reset the imageUploaded variable after processing
            self.imageUploaded = ''

        # Save the test results to a file
        with open(f'test_results/{setname}.json', 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=4)

    # Clear the chat history
    self.chatHistory.config(state='normal')  # Enable editing temporarily
    self.chatHistory.delete(1.0, "end")  # Clear the chat history
    self.chatHistory.see("end")  # Scroll to the bottom
    self.chatHistory.insert("end", f"Finished testing, results saved to test_results.json\n")
    self.chatHistory.config(state='disabled')  # Make it read-only again






