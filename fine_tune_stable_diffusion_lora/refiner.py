from PIL import Image
import torch
from diffusers import DiffusionPipeline, AutoencoderKL, StableDiffusionXLImg2ImgPipeline
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

prompt = "A photo of virat sit in a office ,4k,"

seed = 65
generator = torch.Generator("cuda").manual_seed(seed)
image_output = pipe(prompt=prompt, num_inference_steps=25, generator=generator)

# Extract the image data
image = image_output.images[0]

# Create a folder to save the images
folder_name = "refiner_images"
os.makedirs(folder_name, exist_ok=True)

# Generate timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

# Save and display the original generated image
img_name = f"original_generated_image_{timestamp}.jpg"
img_path = os.path.join(folder_name, img_name)
image.save(img_path)  # Save original image to folder
image.show()

# Refine the generated image
refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-refiner-1.0",
    vae=vae,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16",
)
refiner.to("cuda");

refined_image = refiner(prompt=prompt, num_inference_steps=25, generator=generator, image=image)

# Save and display the refined image
img_name = f"refined_generated_image_{timestamp}.jpg"
img_path = os.path.join(folder_name, img_name)
refined_image.images[0].save(img_path)  # Save refined image to folder
refined_image.images[0].show()  # Display refined image
