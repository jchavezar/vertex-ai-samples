#%%
from vertexai.vision_models import ImageQnAModel, Image

model = ImageQnAModel.from_pretrained("imagetext@001")
image = Image.load_from_file("ad.png")
answers = model.ask_question(
    image=image,
    question="List me all the elements from this image",
    # Optional:
    number_of_results=1,
)

print(answers)
# %%
