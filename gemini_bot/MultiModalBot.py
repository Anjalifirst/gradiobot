import os
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
        You are an helpful Polite FinancialAI Assitant. Answer user queries with below guidelines.
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


# -----------------------------------------------------------------------------------------------------
def gemini_response(gr_message, history):
    """
    Get Chat Response from the Gemini Chatbot.
    """
    # Extract the message and List of Files
    text_message = gr_message.get("text")
    file_list = gr_message.get('files')

    # create message
    message = [str(text_message)] + [T.FileData(file_uri=f, mime_type=f.type) for f in file_list]
    response = my_chat.send_message(message)

    # Check the parts in the response if text respond text, if image show image  any other as file
    # return response.function_calls
    # return response.executable_code
    # return response.code_execution_result
    return response.text


# Define the Bot
with gr.Blocks() as demo:
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
