import gradio as gr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Simple chatbot function
def greet(message, history):
    """Chatbot function that responds to predefined messages."""
    history = history or []
    message = message.lower()

    responses = {
        "hello": "Hello, how can I help you?",
        "how are you": "I'm doing well, thank you for asking.",
        "bye": "Goodbye! Have a great day."
    }
    # Get response from predefined dictionary

    response = responses.get(message, "I'm not sure how to respond to that.")
    history.append((message, response))
    return history, history # Return updated chat history


# Sepia filter function
def sepia(input_img):
    """Applies a sepia filter to an input image."""
    sepia_filter = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    sepia_img = input_img.dot(sepia_filter.T)
    sepia_img /= sepia_img.max()
    return sepia_img # Return processed image


# PDF processing function
def process_pdf(file):
    """Processes a PDF file and returns its name."""
    return f"Received file: {file.name}" # Return file name


# Balance sheet visualization function
def plot_balance_sheet(file):
    """Reads a CSV file and generates a bar plot representing financial data."""
    df = pd.read_csv(file.name)  # Read CSV file

    if "Category" not in df.columns or "Amount" not in df.columns:
        return "Error: CSV must contain 'Category' and 'Amount' columns."

    # Create bar plot of financial categories
    fig, ax = plt.subplots()
    ax.bar(df["Category"], df["Amount"], color=['blue', 'red', 'green'])  
    ax.set_ylabel("Amount ($)")
    ax.set_title("Balance Sheet Overview")

    return fig  # Return the bar plot


# Creating separate interfaces for each function

# Chatbot Interface
text_interface = gr.Interface(
    fn=greet, 
    inputs=[gr.Textbox(lines=2, placeholder="Enter your message"), gr.State()], 
    outputs=[gr.Chatbot(), gr.State()]
)

# Image Processing Interface (Sepia filter)
image_interface = gr.Interface(
    fn=sepia, 
    inputs=gr.Image(type="numpy"), 
    outputs="image"
)

# PDF File Processing Interface
pdf_interface = gr.Interface(
    fn=process_pdf, 
    inputs=gr.File(file_types=[".pdf"]), 
    outputs="text"
)

# Balance Sheet Plotting Interface
plot_interface = gr.Interface(
    fn=plot_balance_sheet, 
    inputs=gr.File(file_types=[".csv"]), 
    outputs="plot"
)


# Combining all interfaces into a single tabbed layout
demo = gr.TabbedInterface(
    [text_interface, image_interface, pdf_interface, plot_interface], 
    ["Chatbot", "Image Processing", "PDF Handler", "Balance Sheet Plotter"]
)


# Launch Gradio application
demo.launch()


