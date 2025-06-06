from ollama import chat

from modules.LLM.constants import VISUAL_MODEL, SYSTEM_PROMPT_IMAGE
from modules.LLM.constants import TEMPERATURE


def analyse_image(image_base64: str) -> str:
    """
    This function is used to analyse the image uploaded by the user. It
    takes the image in base64 format and sends it to the LLM. The LLM 
    will then respond with the actions to be taken.

    :param image_base64: The image in base64 format
    :return: A string containing the analysis of the image
    """
    response = chat(
        model=VISUAL_MODEL,
        messages=[
            {
                'role': 'system',
                'content': SYSTEM_PROMPT_IMAGE
            },
            {
                'role': 'user',
                'content': "Describe how to construct the network topology based on the image.",
                'images': [image_base64],
            }
        ],
        options={"temperature": TEMPERATURE}
    )
    return response.message.content
