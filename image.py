import torch
import time
from diffusers import StableDiffusionPipeline

device = "cpu"
print("Running on CPU. This may be slow.")

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float32
)
pipe.to(device)

timestamp = int(time.time())
filename = f"{timestamp}.png"

prompt = "Virat Kohli scores century against Pakistan"
image = pipe(prompt).images[0]

image.save(filename)
print(f"Image saved as {filename}") 
