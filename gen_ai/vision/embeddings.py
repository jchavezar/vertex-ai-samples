#%%
import os
import re
import scann
import numpy as np
from vertexai.vision_models import MultiModalEmbeddingModel, Image

images = [i for i in os.listdir() if re.match(r".*.png", i)]
    
_embeddings = []

for i in images:
    print(i)
    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
    image = Image.load_from_file(i)

    embeddings = model.get_embeddings(
        image=image,
        contextual_text="",
    )
    image_embedding = embeddings.image_embedding
    text_embedding = embeddings.text_embedding
    
    _embeddings.append(image_embedding)

#print(image_embedding)
# %%
index = np.empty((len(_embeddings), len(_embeddings[0])))
normalized_index = index / np.linalg.norm(index, axis=1)[:, np.newaxis]

for i in range(index.shape[0]):
    index[i] = _embeddings[i]   

#%%
builder = scann.scann_ops_pybind.builder(
    normalized_index, # index
    2, # num_neighbors
    "dot_product" # distance_measure
    )
k = int(np.sqrt(index.shape[0]))

searcher = builder.tree(
    num_leaves=k, #num_leaves
    num_leaves_to_search=int(2), #num_leaves_to_search
    training_sample_size=index.shape[0]
    ).score_ah(
      2,
      anisotropic_quantization_threshold=0.2
      ).reorder(
          index.shape[0]
          ).build()
      
def search_index(query, k):
    neighbors, distances = searcher.search(query, final_num_neighbors=k)
    return list(zip(neighbors, distances))

_text_embeddings = model.get_embeddings(
    image="",
    contextual_text="an add showing christmas pillows",
).text_embedding

print(search_index(_text_embeddings, 2))
