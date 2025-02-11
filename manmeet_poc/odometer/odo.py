import gradio as gr
import base64
import requests
import io
import os
from PIL import Image

# Get the OpenAI API key from the environment variables
api_key = "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"

# Function to encode image to base64
def encode_image(image):
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

# Function to process image and get odometer reading
def get_odometer_reading(image):
    try:
        # Convert uploaded image to base64
        base64_image = encode_image(image)
        
        if not base64_image:
            return "Error encoding the image."

        # Setup headers for OpenAI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Prepare the request payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Tell me the exact reading in the odometer and return the number only. if you can't get the required number then honestly response with 'Unable to find number'"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 50
        }

        # Send request to OpenAI API
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to find number')
        else:
            return f"API Error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error processing the image: {str(e)}"

# Function to calculate total distance
def calculate_distance(initial_image, final_image):
    try:
        initial_reading = get_odometer_reading(initial_image)
        final_reading = get_odometer_reading(final_image)

        try:
            initial_value = int(initial_reading) if initial_reading.isdigit() else None
            final_value = int(final_reading) if final_reading.isdigit() else None

            if initial_value is not None and final_value is not None:
                total_distance = final_value - initial_value
                return initial_reading, final_reading, total_distance
            else:
                return initial_reading, final_reading, "Unable to calculate total distance."
        except Exception as e:
            return initial_reading, final_reading, f"Error calculating distance: {e}"
    except Exception:
        return "Error processing images.", "", ""
    
static_image_path = "odo.png"
static_image = Image.open(static_image_path)

# Gradio app
with gr.Blocks() as demo:
    gr.Markdown("## Odometer Reading Tool")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Initial Odometer Reading")
            initial_image_input = gr.Image(type="pil", label="Upload Initial Image")

        with gr.Column():
            gr.Markdown("### Final Odometer Reading")
            final_image_input = gr.Image(type="pil", label="Upload Final Image")

    submit_button = gr.Button(" Calculate")

    with gr.Row():
        initial_description_output = gr.Textbox(label="Initial Reading", lines=2)
        final_description_output = gr.Textbox(label="Final Reading", lines=2)

    total_distance_output = gr.Textbox(label="Total Travel Distance", lines=1)

    submit_button.click(
        fn=calculate_distance,
        inputs=[initial_image_input, final_image_input],
        outputs=[
            initial_description_output,
            final_description_output,
            total_distance_output
        ]
    )
    
    gr.Markdown("### Reference Image")
    gr.Image(value=static_image, label="Image")

# Launch the app
demo.launch()
