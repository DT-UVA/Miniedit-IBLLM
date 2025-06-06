from tkinter import Frame, Text, Label, Scrollbar
from mininet.log import info
from tkinter import filedialog
import base64

def create_chat_window(self):
    """
    Create the chat window for the GUI.
    This function sets up the layout and widgets for the chat interface,
    including a text area for chat history, an input field for user input,
    and a submit button to send messages.
    """
    # Chatwindow
    self.chatFrame = Frame(self, bg='white', width=300)
    self.chatFrame.grid_propagate(False)  # Prevent resizing
    self.chatFrame.columnconfigure(0, weight=1)
    self.chatFrame.rowconfigure(0, weight=6)
    self.chatFrame.rowconfigure(1, weight=3)
    self.chatFrame.rowconfigure(2, weight=1)
    self.chatFrame.rowconfigure(3, weight=1)

    # Add a scrollbar for the non-editable text area
    self.historyScrollbar = Scrollbar(self.chatFrame)
    self.historyScrollbar.grid(row=0, column=1, sticky='ns')

    # Add a non-editable text widget for chat history
    self.chatHistory = Text(self.chatFrame, font=self.font, bg='lightgray',
                            wrap='word', yscrollcommand=self.historyScrollbar.set, state='disabled')
    self.chatHistory.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    self.historyScrollbar.config(command=self.chatHistory.yview)

    # Add a scrollbar to the chatFrame
    self.scrollbar = Scrollbar(self.chatFrame)
    self.scrollbar.grid(row=1, column=1, sticky='ns')

    # Add a text widget to the chatframe
    self.chatText = Text(self.chatFrame, font=self.font, bg='white',
                         wrap='word', yscrollcommand=self.scrollbar.set, height=5)
    self.chatText.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
    self.scrollbar.config(command=self.chatText.yview)
    # When pressing enter, send the text
    self.chatText.bind('<Return>', lambda event: self.submit_chat())

    # Add a submit button to send the text
    self.submitButton = Label(
        self.chatFrame, text='Submit prompt', font=self.font, bg='lightgray', relief='raised')
    self.submitButton.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
    self.submitButton.bind('<Button-1>', lambda event: self.submit_chat())

    # Add a file upload button
    self.fileUploadButton = Label(
    self.chatFrame, text='Upload Image', font=self.font, bg='lightgray', relief='raised')
    self.fileUploadButton.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
    self.fileUploadButton.bind('<Button-1>', lambda event: self.upload_image())
    self.imageUploaded = ''

    return self.chatFrame


def upload_image(self):
    """
    Open a file dialog to select an image file and convert it to a base64 string.
    This function will check if the selected file is an image based on its extension.
    If the file is an image, it will be read and converted to a base64 string.
    The base64 string will be stored in the instance variable imageUploaded.
    """
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename()

    # Check if the file selected is an image
    if file_path:
        # Use string methods to check if the file is an image
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            with open(file_path, 'rb') as image_file:
                # Read the image file
                image_data = image_file.read()
                # Convert the image data to a base64 string
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                # Store the base64 string in the instance variable
                self.imageUploaded = image_base64

                # Set the upload button text to the file name
                self.fileUploadButton.config(text=file_path.split('/')[-1])


def submit_chat(self):
    """
    Handle the submission of chat input.
    This function retrieves the content from the chat text area,
    clears the text area, and processes the input based on whether
    an image has been uploaded or not. If an image is uploaded,
    it calls the LLMChatImage function; otherwise, it calls the LLMChat function.

    param self: The instance of the class.
    return: The result of the LLMChat or LLMChatImage function.
    """

    # Get the content of the chat text area
    prompt = self.chatText.get("1.0", "end").strip()

    if len(prompt) > 0:
        # Call the function to handle the chat
        handle_chat(self, prompt)

        # Check if an image has been uploaded
        if len(self.imageUploaded) > 0:
            result = self.LLMChat()
            
            # Reset the imageUploaded variable after processing
            self.imageUploaded = ''

            # Reset the upload button text to default
            self.fileUploadButton.config(text='Upload Image')

            # Return the result of the LLMChat function
            return result

        else:
            # Call the function to handle the text
            return self.LLMChat()
        

def handle_chat(self, prompt):
    """
    Handle the chat input by appending it to the chat history and updating the chat text area.
    This function is responsible for managing the chat history and ensuring that the chat text area is cleared
    after the user submits a message. It also ensures that the chat history is scrollable and that the cursor
    is reset to the first row after submission.
    :param self: The instance of the class.
    :param prompt: The user input from the chat text area.
    :return: None
    """
    # Append the user prompt to the chat history
    self.chat_history.extend([
        {'role': 'user', 'content': prompt},
    ])

    # Append the submitted chat to the chat history
    self.chatHistory.config(state='normal')  # Enable editing temporarily
    self.chatHistory.insert("end", f"User: {prompt}\n")
    self.chatHistory.config(state='disabled')  # Make it read-only again
    self.chatHistory.see("end")  # Scroll to the bottom

    # Clear the chat text area
    self.chatText.delete("1.0", "end")

    # Reset the cursor to the first row
    self.chatText.mark_set("insert", "1.0")
    self.chatText.focus()  # Set focus back to the chat text area


