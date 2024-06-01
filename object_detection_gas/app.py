import gradio as gr
import torch
from PIL import Image

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', _verbose=False)
model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')

def yolo(im, size=640):
    g = (size / max(im.size))
    im = im.resize((int(x * g) for x in im.size), Image.ANTIALIAS)  # resize

    results = model(im)
    results.render()
    a = results.pandas().xyxy[0]
    z = a.name.value_counts().to_string()
    if z == "Series([], )":
        z="No object detected"
    return z, Image.fromarray(results.ims[0])

inputs = gr.inputs.Image(type='pil', label="Original Image")
outputs = [gr.Textbox(label="Objects deteted"), gr.outputs.Image(type="pil", label="Detections in the image")]

gr.Interface(yolo, inputs, outputs, analytics_enabled=False).launch(
    debug=True)
