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
import pandas as pd


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
    mime_type, _ = mimetypes.guess_type(file_path)
    if file_path.endswith(".csv"):
        mime_type = "text/plain"  # Treat CSV as text
    return mime_type


def get_file_bytes(file_path):
    """Extract text from CSV files before sending to Gemini."""
    mime_type = get_mime_type(file_path)

    if mime_type == "text/csv":
        df = pd.read_csv(file_path)  # Read CSV file
        return df.to_string()  # Convert DataFrame to a readable text format

    with open(file_path, "rb") as file:
        file_bytes = file.read()

    return T.Part.from_bytes(data=file_bytes, mime_type=mime_type) if mime_type else None


# Global variable to store latest PDF path
latest_pdf_path = None

def create_pdf_output(text, filename="FinGPT_Response.pdf"):
    """Generate a temporary PDF file from chatbot response."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, text)

    # Create a temp directory & assign a specific filename
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, filename)

    pdf.output(pdf_path)
    return pdf_path  # Returns path for download

# -----------------------------------------------------------------------------------------------------
def gemini_response(gr_message, history):
    """Get Chat Response from the Gemini Chatbot, while storing responses as PDFs."""

    global latest_pdf_path  # Keep track of the last PDF

    # Extract the text and files from the input
    text_message = gr_message.get("text", "")
    file_list = gr_message.get("files", [])

    # Return last generated PDF 
    if text_message.strip().lower() == "generate pdf":
        if latest_pdf_path:
            return {"text": "Here is your PDF:", "files": [latest_pdf_path]}
        else:
            return {"text": "No PDF has been generated yet."}
    
    # Attach valid files (if any)
    message_attachments = []
    for f in file_list:
        file_path = Path(f)
        if file_path.exists():
            file_data = get_file_bytes(file_path=f)
            if file_data is not None:
                message_attachments.append(file_data)

    # Send message to Gemini chatbot
    message = [str(text_message)] + message_attachments
    response = my_chat.send_message(message)
    response_text = response.text.strip()

    # Always generate a PDF from the response
    latest_pdf_path = create_pdf_output(response_text)

    # Otherwise return just the text
    return response.text

# -----------------------------------------------------------------------------------------------------
# Define the Bot
with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("# FinGPT Bot")
    gr.Markdown("""
    I am a Helpful AI Assistant. Here's what I can do:
    - Answer **financial-related questions**.
    - Analyze **uploaded images** (describe the content).
    - Process **financial PDFs & CSVs** (extract insights, answer questions).
    - **To download your response as a PDF**, type `"generate PDF"`.             
    """)
    gr.ChatInterface(
        # title="Multimodal ChatBot",
        fn=gemini_response,
        multimodal=True,
        type="messages",
    )

# Launch the Bot
demo.launch()