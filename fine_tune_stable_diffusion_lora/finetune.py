from PIL import Image
import torch
from diffusers import DiffusionPipeline, AutoencoderKL
import os
from datetime import datetime

PROJECT_NAME = "dreambooth_project"
MODEL_NAME = "stabilityai/stable-diffusion-xl-base-1.0"
REPO_ID = "anushvst/virat"

# Define the VAE and the diffusion pipeline
vae = AutoencoderKL.from_pretrained(
    "madebyollin/sdxl-vae-fp16-fix", 
    torch_dtype=torch.float16
)
pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    vae=vae,
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True,
)
pipe.to("cuda")
pipe.load_lora_weights(REPO_ID, weight_name="pytorch_lora_weights.safetensors")

# Define the prompt
prompt = "A photo of virat sit on horse,4k"

# Generate images based on the prompt
image = pipe(prompt=prompt, num_inference_steps=25, num_images_per_prompt=3)

# Create a folder to save the images
folder_name = "generated_images"
os.makedirs(folder_name, exist_ok=True)

# Generate timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

# Display and save generated images
for i, img in enumerate(image.images):
    img_name = f"generated_image_{i}_{timestamp}.jpg"
    img_path = os.path.join(folder_name, img_name)
    img.save(img_path)  # Save image to folder
    img.show()
