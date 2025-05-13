import io
import random

import gradio as gr
import matplotlib.pyplot as plt
from PIL import Image


def generate_chart():
    "Return a Random Chart Object"
    fig, ax = plt.subplots()
    x = list(range(100))
    y = [random.uniform(0, 10) for _ in x]
    ax.plot(x, y, marker='o')
    ax.set_title("Random Line Chart")

    # Convert Chart to Image
    # TODO: Add Image size as per the screen
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img = Image.open(buf)
    return gr.Image(img)


def get_image():
    "Return an Image Object"
    return gr.Image("Aiyya.jpg")


def respond(message, history):
    """
    My Chatbot Function That Can Be Customised to Anything.
    """
    # Extract the message and List of Files
    text_message = message.get("text")
    file_message = message.get('files')

    # Respond as needed.
    if text_message.strip().lower() == 'hi':
        return "Hello"
    elif text_message.strip().lower() == 'show_history':
        return f"Here is Your History:{history}"
    elif text_message.strip().lower() == 'show_files':
        return [f"Here is Your file list:{file_message}\n", gr.File(file_message[0]) if file_message else ""]
    elif text_message.strip().lower() == 'show_image':
        return [get_image(), "Here is your Image."]
    elif text_message.strip().lower() == 'show_chart':
        return [generate_chart(), "Here is Your Chart"]
    else:
        return "Oops !! Try Show_image for a cute one :-) !!"


# Define the Bot
with gr.Blocks() as demo:
    gr.Markdown("# FinGPT Bot")
    gr.Markdown("""
    We can do all these with the FinGPT.
    
        - Say Hi
        - SHOW_IMAGE
        - SHOW_CHART
        - SHOW_FILES
        - SHOW_HISTORY 
        
    """)
    gr.ChatInterface(
        # title="Multimodal ChatBot",
        fn=respond,
        multimodal=True,
        type="messages",
        # description="Try commands like 'hi', 'SHOW_IMAGE', or 'SHOW_CHART' or 'SHOW_FILES', 'SHOW_HISTORY' You can also upload a file.",
    )

# Launch the Bot
demo.launch()
