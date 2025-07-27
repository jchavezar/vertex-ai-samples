#%%
import numpy as np
import tensorflow_hub as hub

# ScaNN
# Generate a synthetic dataset of 1 million vectors
NUM_VECTORS = 10000
VECTOR_DIM = 128

q_v_list = [-0.14690647,  0.3276665 ,  1.0102983 , -1.2282795 ,  0.89248556,
       -0.07906895,  0.4466771 , -0.76008207,  1.0265373 ,  0.01717316,
       -0.24289595,  0.8514989 , -0.5655282 ,  0.20507611, -0.77004325,
       -1.2363168 , -0.28874415, -0.536672  ,  0.8847661 ,  0.10183878,
       -0.11081283, -1.1898361 , -1.3826481 ,  0.9965114 ,  0.15745945,
        0.3659046 ,  2.0643134 ,  0.10708047, -2.3419807 , -1.5830019 ,
        0.22151579, -0.9721361 , -0.25590518,  2.293204  ,  1.716308  ,
       -2.1752105 ,  0.5527758 ,  0.35040003, -0.10843611,  2.8124092 ,
       -1.4494935 , -0.27978814, -1.986276  , -1.2217535 , -0.4273323 ,
        0.2339908 , -0.4881549 ,  1.0538608 ,  0.3583856 ,  0.15234813,
       -0.48396927,  0.995227  ,  1.7623534 , -0.9089539 ,  0.66716504,
       -0.6345837 ,  0.83754104,  0.6126466 ,  1.6528963 , -1.0272479 ,
       -0.79677916, -2.2741396 ,  0.7468287 , -0.34147838, -1.0505369 ,
        0.6325583 , -0.6278732 ,  2.412636  ,  0.0187083 ,  0.3157298 ,
        1.1224841 , -0.85933244, -1.7239467 ,  0.3683148 ,  2.3473995 ,
        0.37852785, -1.4821981 , -0.16842218,  0.7997589 , -0.58388126,
        1.2091247 ,  1.1925865 , -1.0183598 , -1.1985477 ,  0.85748464,
        0.02685928,  0.71865284, -1.5879298 , -0.2168916 ,  1.6967856 ,
        0.14800237,  0.8684257 ,  1.3632474 ,  1.1788913 ,  0.9011258 ,
        0.55091023, -0.21373956, -2.2355716 , -0.856703  , -0.2804531 ,
        1.9972414 ,  0.31852055, -1.0503744 ,  1.8273005 ,  0.89291966,
       -0.63718563,  0.42727563, -0.11045792,  1.3493465 , -0.10590056,
       -0.5767269 , -0.7180307 ,  1.5747211 , -0.986903  ,  0.469874  ,
        1.8305314 ,  0.01022509,  0.42855167,  0.21506198, -0.75663835,
       -0.27670237, -0.38731855,  0.38144213, -0.9686395 , -0.4551952 ,
       -0.9047083 ,  0.33471873,  1.2496629]

query_vector = np.array(q_v_list, dtype=np.float32)

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)

#with open("dataset.npy", "rb") as f:
#    dataset = np.load(f)

#%%
import numpy as np
import tensorflow as tf
import scann
import os

data = [
    "I like cats", 
    "I like dogs",
    "I like squirrels",
    "I am a cow",
    "You are a miau",
    "You muu",
    "Are you a turtle?",
    "would you like to be a bear",
    "You like whales",
    "You are a Tiger",
    "The elephant is big",
    "The jiraf is tall",
    "The monkey jumps",
    "Gorilla also jumps",
    "I am John",
    "I am Doe"
    ]
dataset = model(data).numpy()
_dataset = [{d:dataset[n]} for n,d in enumerate(data)]
query_vector = model(["John is a good Turtle"]).numpy().reshape([512])

# Build a ScaNN index with L2 distance metric and 10 random projection hash tables
searcher = scann.scann_ops_pybind.builder(dataset, num_neighbors=10, distance_measure="squared_l2").tree(
    num_leaves=16, num_leaves_to_search=16, training_sample_size=16).score_ah(
    2, anisotropic_quantization_threshold=0.2).reorder(4).build()

# Create a directory for the serialized index
if not os.path.exists("scann_index"):
    os.makedirs("scann_index")

# Save the index to disk
searcher.serialize("scann_index")

# Load the index from disk
#searcher = scann.scann_ops_pybind.load_searcher("scann_index/")

# Generate a query vector

# Find the top 10 nearest neighbors of the query vector
k = 10
neighbors, distances = searcher.search(query_vector, final_num_neighbors=k)

# neighbours is an array of indexes for nearest neighbors. distances is an array with their corresponding squared_L2 distnaces
neighbors,distances

print(_dataset[neighbors[0]])
# %%

#Facebook FAISS

import numpy as np
import faiss

# Generate a synthetic dataset of 1 million vectors
#NUM_VECTORS = 10000
#VECTOR_DIM = 128
#
#dataset = np.random.randn(NUM_VECTORS, VECTOR_DIM).astype(np.float32)

quantizer = faiss.IndexFlatL2(VECTOR_DIM)
nlist=10
m=16
nbits=8
index = faiss.IndexIVFPQ(quantizer,VECTOR_DIM, nlist, m, nbits)

# Train the index on a random subset of the dataset
subset_size = 10000
subset = dataset[np.random.choice(NUM_VECTORS, subset_size, replace=False)]
index.train(subset)

# Add the full dataset to the index
index.add(dataset)

# Generate a query vector
#query_vector = np.random.randn(1, VECTOR_DIM).astype(np.float32)
query_vector_2 = np.reshape(query_vector, (1,128))
# Find the top 10 nearest neighbors of the query vector
k = 10
distances, neighbors = index.search(query_vector_2, k)

# Print the top 10 nearest neighbors
for i, neighbor in enumerate(neighbors[0]):
    print("Neighbor {}: distance={}".format(neighbor, distances[0][i]))
# %%
