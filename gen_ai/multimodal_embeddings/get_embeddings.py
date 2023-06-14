#%%
import numpy as np
from numpy.linalg import norm

from utils.llm import Embeddings

text_emb = Embeddings(text="car",project="vtxdemos")
image_emb = Embeddings(image_file="car.jpg",project="vtxdemos")

# %%
cosine = np.dot(text_emb,image_emb)/(norm(text_emb)*norm(image_emb))
print("Cosine Similarity:", cosine)

# %%
