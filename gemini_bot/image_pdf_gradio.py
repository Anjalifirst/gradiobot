import PIL.Image
# Gemini related packages
from google import genai
from google.genai import types
import gradio as gr

# API Key is added
GOOGLE_API_KEY = ""
# Step 1: Initialize Gemini API
# Define model ID
model_id = "gemini-2.0-flash"
# Initialize the Gemini API client
client = genai.Client(api_key=GOOGLE_API_KEY)
new_client = client.chats.create()

# Step 2: Create a function to process images
def process_image(image_path, prompt_choice):
    if not isinstance(image_path, str):  # Validate input
        raise ValueError("Invalid file format")

    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()

    prompt_options = {
        "Describe Image": "Describe this image in detail.",
        "Identify Objects": "Identify and list objects in this image.",
        "Explain Scene": "Explain what is happening in this image."
    }

    prompt_text = prompt_options.get(prompt_choice, "Describe Image")

    response = client.models.generate_content_stream(
        model = model_id,
        contents = [
            types.Part.from_bytes(
                data = img_bytes,
                mime_type = 'image/png'
            ),
            prompt_text
        ]
    )

    full_response = ""
    for chunk in response:
        full_response += chunk.text

    return full_response

# Create a function that processes PDFs into prompts
model_id = 'gemini-2.0-flash'
def process_pdf(pdf_file, prompt_choice):

  if isinstance(pdf_file, dict) and "name" in pdf_file:
    file_path = pdf_file["name"]
  elif isinstance(pdf_file, str):
    file_path = pdf_file
  else:
    raise ValueError("Invalid file format")

  with open(file_path, 'rb') as f:
    pdf_bytes = f.read()

  prompt_options = {
      "Summarize Document": "Summarize this document for me."
  }

  prompt_text = prompt_options.get(prompt_choice, "Summarize Document")

  response = client.models.generate_content_stream(
      model = model_id,
      contents = [
          types.Part.from_bytes(
              data = pdf_bytes,
              mime_type = 'application/pdf'
          ),
          prompt_text
      ]
  )

  full_response = ""
  for chunk in response:
    full_response += chunk.text

  return full_response

with gr.Blocks() as demo:
    # Title and description for the application
    gr.Markdown("# FinTech application")
    gr.Markdown("Select a tab to process either a PDF or Image file")

    with gr.Tabs():
        #-------------- PDF Processing Tab -----------------
        with gr.Tab("PDF Processing"):
            gr.Markdown("**Upload a PDF file and select a prompt.**")

            # File uploader for PDF files
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])

            # Radio button to select a processing prompt for the PDF
            pdf_prompt = gr.Radio(
                choices = ["Summarize Document"],
                label = "Select PDF Prompt",
                value = "Summarize Document" # Default selected option
            )

            # Textbox to display the generated response
            pdf_output = gr.Textbox(label="Response", lines=10)

            # Button to trigger PDF processing
            pdf_button = gr.Button("Process PDF")

            # clicking the button triggers the 'process_pdf'function
            pdf_button.click(fn=process_pdf, inputs=[pdf_input, pdf_prompt], outputs=pdf_output)


        with gr.Tab("Image Processing"):
            gr.Markdown("**Upload an image and choose a prompt.**")

            # File uploader for images
            image_input = gr.File(label="Upload Image", file_types=[".png", ".jpg", ".jpeg"])

            # Radio button to select a processing prompt for the image
            image_prompt = gr.Radio(
                choices=["Describe Image", "Identify Objects", "Explain Scene"],
                label="Select Image Processing Prompt",
                value="Describe Image"  # Default selected option
            )

            # Textbox to display the generated response
            image_output = gr.Textbox(label="AI Response", lines=10)

            # Button to trigger image processing
            image_button = gr.Button("Process Image")

            # Clicking the button triggers the 'process_image' function
            image_button.click(fn=process_image, inputs=[image_input, image_prompt], outputs=image_output)

# Enable the queue to handle long-running functions
demo.queue()

# Step 2: Launch the Gradio app
demo.launch(debug=True)