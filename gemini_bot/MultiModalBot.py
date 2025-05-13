import mimetypes
import os
from pathlib import Path
from textwrap import dedent

import gradio as gr
from dotenv import load_dotenv
from google import genai
from google.genai import types as T

# -----------------------------------------------------------------------------------------------------
# Get Confs
load_dotenv(verbose=True)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL_ID = os.environ.get("MODEL_ID")
client = genai.Client(api_key=GOOGLE_API_KEY)

# -----------------------------------------------------------------------------------------------------
# New Chat Session
# TODO: Customer ID based chat sessions.
my_chat = client.chats.create(
    model=MODEL_ID,
    config={
        "system_instruction": dedent("""
        You are an helpful polite Financial AI Assitant. Answer user queries with below guidelines.
        Guidelines:
         - Don't Respond questions that are not related to Finance.
         - Only handle files that are PDF, CSV, and Image.
         - Incase of Charts to be Shown. Please respond with a chart Image.
        """),
        "temperature": 0.5,
        "max_output_tokens": 1000,
        "top_p": 0.8,
        "top_k": 40,
    },
    history=[]
)


def get_mime_type(file_path):
    """
    Get the MIME type of a file.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type


def get_file_bytes(file_path):
    """
    Get the bytes of a file.
    else return None
    """
    with open(file_path, "rb") as file:
        file_bytes = file.read()

    mime_type = get_mime_type(file_path)
    if mime_type is None:
        return None
    return T.Part.from_bytes(data=file_bytes, mime_type=mime_type)


# -----------------------------------------------------------------------------------------------------
def gemini_response(gr_message, history):
    """
    Get Chat Response from the Gemini Chatbot.
    """
    # Extract the message and List of Files
    text_message = gr_message.get("text")
    file_list = gr_message.get('files', [])

    # Check if the file is a valid type else don't attach.
    message_attachments = []
    for f in file_list:
        file_path = Path(f)
        if file_path.exists():
            file_data = get_file_bytes(file_path=f)
            if file_data is not None:
                message_attachments.append(file_data)
    # create message
    message = [str(text_message)] + message_attachments
    response = my_chat.send_message(message)

    # Check the parts in the response if text respond text, if image show image  any other as file
    print("Funcs:", response.function_calls)
    print("Code:", response.executable_code)
    print("Code_Results:", response.code_execution_result)
    return response.text


# Define the Bot
with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("# FinGPT Bot")
    gr.Markdown("""
    I am a HelpFul AI Assistant. Try me.
    - Ask Financial Questions
    - Upload a Image and ask to describe it.
    - Upload a Financial PDF and ask questions on it.     
    """)
    gr.ChatInterface(
        # title="Multimodal ChatBot",
        fn=gemini_response,
        multimodal=True,
        type="messages",
    )

# Launch the Bot
demo.launch()
