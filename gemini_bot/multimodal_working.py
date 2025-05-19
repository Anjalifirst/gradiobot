from fpdf import FPDF
import mimetypes
import os
from pathlib import Path
from textwrap import dedent
import tempfile
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

from pathlib import Path
from typing import Dict, Any, List

from fpdf import FPDF
import tempfile

from fpdf import FPDF
import tempfile
from pathlib import Path

# Global variable to store latest PDF path
latest_pdf_path = None

def create_pdf_output(text):
    """Generate a temporary PDF file from chatbot response."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, text)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        pdf_path = temp_file.name
        pdf.output(pdf_path)

    return pdf_path  # ✅ Returns path for download


def gemini_response(gr_message, history):
    """Get Chat Response from the Gemini Chatbot, while storing responses as PDFs."""

    global latest_pdf_path  # ✅ Keep track of the last PDF

    # Step 0: Extract the text and files from the input
    text_message = gr_message.get("text", "")
    file_list = gr_message.get("files", [])

    # Step 1: Check if the user is requesting a PDF
    if "pdf" in text_message.lower():
        return {"text": "", "files": [latest_pdf_path]}  # ✅ Serve PDF on request

    # Step 1: Attach valid files (if any)
    message_attachments = []
    for f in file_list:
        file_path = Path(f)
        if file_path.exists():
            file_data = get_file_bytes(file_path=f)
            if file_data is not None:
                message_attachments.append(file_data)

    # Step 2: Send message to Gemini chatbot
    message = [str(text_message)] + message_attachments
    response = my_chat.send_message(message)

    # Step 4: Create PDF only if response is valid
    response_text = response.text.strip()
    if "cannot provide the pdf" not in response_text.lower():
        latest_pdf_path = create_pdf_output(response_text)
    

    # Step 5: Otherwise return just the text
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