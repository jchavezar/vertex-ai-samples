#%%
from vertexai.vision_models import ImageCaptioningModel, Image

model = ImageCaptioningModel.from_pretrained("imagetext@001")
image = Image.load_from_file("ad.png")
captions = model.get_captions(
    image=image,
    # Optional:
    number_of_results=1,
    language="en",
)

print(captions)
# %%
