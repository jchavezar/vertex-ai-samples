#%%
import os
import scann
import vertexai
import numpy as np
import tensorflow_hub as hub
from vertexai.language_models import TextEmbeddingModel

# ScaNN
# Generate a synthetic dataset of 1 million vectors
NUM_VECTORS = 10000
VECTOR_DIM = 128

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
encoder_model = hub.load(module_url)

table = [
    """
    Table Name: assets
    Table description : assets table contains movies and series information.
    column information:
        column_name,data_type,description
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "name","varchar(50)","name of the movie or series"
        "imdb_id","varchar(50)","Unique identifier of the imdb_id.imdb_id starts with a prefix 'tt'."
        "type","varchar(50)","type of the asset.This can only be one of the following values:['MOVIE','SERIES']"
        "original_language","varchar(50)","original language of the asset "
        "rating","varchar(50)","rating of the asset"
        "release_date","varchar(50)","release date of the asset.Date is in the format of yyyy-MM-dd for example 2023-10-01"
        "runtime","varchar(50)","runtime of the asset"
        "number_of_seasons","varchar(50)","number of seasons in a SERIES"
        "number_of_episodes","varchar(50)","number of episodes in a season"
        "release_type","varchar(50)","release type of the asset.This can only be one of the following values:['MOVIE','EPISODIC']"
        "overview","varchar(50)","over view of the asset"
        "image_url","varchar(50)","image url of the asset"
        "certification","varchar(50)","certification of the asset"
    """,
    """
    Table Name: users
    Table description : users table contains information about the users.
    column information:
        column_name,data_type,description
        "user_id","varchar(50)","Unique identifier of the user.user_id starts with a prefix 'us'."
        "name","varchar(50)","name of the user"
        "email","varchar(50)","email of the user"
        "password","varchar(50)","password of the user"
        "role","varchar(50)","role of the user.This can only be one of the following values:['ADMIN','USER']"
        "created_at","varchar(50)","created date of the user.Date is in the format of yyyy-MM-dd for example 2023-10-01"
        "updated_at","varchar(50)","updated date of the user.Date is in the format of yyyy-MM-dd for example 2023-10-01"
    """,
    """
    Table Name: user_ratings
    Table description : user_ratings table contains information about the ratings given by the users.
    column information:
        column_name,data_type,description
        "user_id","varchar(50)","Unique identifier of the user.user_id starts with a prefix 'us'."
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "rating","varchar(50)","rating given by the user"
        "created_at","varchar(50)","created date of the rating.Date is in the format of yyyy-MM-dd for example 2023-10-01"
        "updated_at","varchar(50)","updated date of the rating.Date is in the format of yyyy-MM-dd for example 2023-10-01"
    """,
    """
    Table Name: watch_history
    Table description : watch_history table contains information about the watch history of the users.
    column information:
        column_name,data_type,description
        "user_id","varchar(50)","Unique identifier of the user.user_id starts with a prefix 'us'."
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "watched_date","varchar(50)","date when the user watched the asset.Date is in the format of yyyy-MM-dd for example 2023-10-01"
        "created_at","varchar(50)","created date of the watch history.Date is in the format of yyyy-MM-dd for example 2023-10-01"
        "updated_at","varchar(50)","updated date of the watch history.Date is in the format of yyyy-MM-dd for example 2023-10-01"
    """,
    """
    Table Name: recommendations
    Table description : recommendations table contains information about the recommendations given to the users.
    column information:
        column_name,data_type,description
        "user_id","varchar(50)","Unique identifier of the user.user_id starts with a prefix 'us'."
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "recommendation_type","varchar(50)","type of the recommendation.This can only be one of the following values:['POPULAR','TRENDING','SIMILAR']"
        "created_at","varchar(50)","created date of the recommendation.Date is in the format of yyyy-MM-dd for example 2023-10-01"
        "updated_at","varchar(50)","updated date of the recommendation.Date is in the format of yyyy-MM-dd for example 2023-10-01"
    """,
    """
    Table Name: genres
    Table description : genres table contains information about the genres of the assets.
    column information:
        column_name,data_type,description
        "genre_id","varchar(50)","Unique identifier of the genre.genre_id starts with a prefix 'gn'."
        "name","varchar(50)","name of the genre
    """,
    """
    Table Name: asset_genres
    Table description : asset_genres table contains information about the genres of the assets.
    column information:
        column_name,data_type,description
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "genre_id","varchar(50)","Unique identifier of the genre.genre_id starts with a prefix 'gn'."
    """,
    """
    Table Name: countries
    Table description : countries table contains information about the countries of the assets.
    column information:
        column_name,data_type,description
        "country_id","varchar(50)","Unique identifier of the country.country_id starts with a prefix 'cy'."
        "name","varchar(50)","name of the country"
    """,
    """
    Table Name: asset_countries
    Table description : asset_countries table contains information about the countries of the assets.
    column information:
        column_name,data_type,description
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "country_id","varchar(50)","Unique identifier of the country.country_id starts with a prefix 'cy'."
    """,
    """
     Table Name: languages
    Table description : languages table contains information about the languages of the assets.
    column inforTable Name: creators
Table description : creators table contains information about the creators of the assets.
column information:
column_name,data_type,description
"creator_id","varchar(50)","Unique identifier of the creator.creator_id starts with a prefix 'cr'."
"name","varchar(50)","name of the creator"mation:
        column_name,data_type,description
        "language_id","varchar(50)","Unique identifier of the language.language_id starts with a prefix 'lg'."
        "name","varchar(50)","name of the language"
    """,
    """
    Table Name: asset_languages
    Table description : asset_languages table contains information about the languages of the assets.
    column information:
        column_name,data_type,description
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "language_id","varchar(50)","Unique identifier of the language.language_id starts with a prefix 'lg'."
    """,
    """
     Table Name: assets
    Table description : assets table contains information about the assets.
    column information:
        column_name,data_type,description
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "title","varchar(50)","title of the asset"
        "description","varchar(50)","description of the asset"
        "release_year","varchar(50)","release year of the asset"
        "duration","varchar(50)","duration of the asset"
        "rating","varchar(50)","rating of the asset"
        "num_views","varchar(50)","number of views of the asset"
        "num_likes","varchar(50)","number of likes of the asset"
        "num_dislikes","varchar(50)","number of dislikes of the asset"
        "num_comments","varchar(50)","number of comments of the asset"
        "num_shares","varchar(50)","number of shares of the asset"
        "created_at","varchar(50)","created date of the asset"
        "updated_at","varchar(50)","updated date of the asset"
    """,
    """
    Table Name: asset_types
    Table description : asset_types table contains information about the types of the assets.
    column information:
        column_name,data_type,description
        "asset_type_id","varchar(50)","Unique identifier of the asset type.asset_type_id starts with a prefix 'at'."
        "name","varchar(50)","name of the asset type"
    """,
    """
    Table Name: asset_asset_types
    Table description : asset_asset_types table contains information about the types of the assets.
    column information:
        column_name,data_type,description
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "asset_type_id","varchar(50)","Unique identifier of the asset type.asset_type_id starts with a prefix 'at'."
    """,
    """
    Table Name: asset_creators
    Table description : asset_creators table contains information about the creators of the assets.
    column information:
        column_name,data_type,description
        "asset_id","varchar(50)","Unique identifier of the asset.asset_id starts with a prefix 'ot'."
        "creator_id","varchar(50)","Unique identifier of the creator.creator_id starts with a prefix 'cr'."
    """,
    """
    Table Name: creators
    Table description : creators table contains information about the creators of the assets.
    column information:
        column_name,data_type,description
        "creator_id","varchar(50)","Unique identifier of the creator.creator_id starts with a prefix 'cr'."
        "name","varchar(50)","name of the creator"
    """ 
]

vertexai.init(project="vtxdemos", location="us-central1")
parameters = {
    "candidate_count": 1,
    "max_output_tokens": 64,
    "temperature": 0.2
}
gecko_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

embeddings = gecko_model.get_embeddings(table)

#%%
dataset = encoder_model(table).numpy()
dataset_2 = [i.values for i in embeddings]
_dataset = [{d:dataset[n]} for n,d in enumerate(table)]
__dataset = [{d:embeddings[n].values} for n,d in enumerate(table)]
query_vector = encoder_model(["How many seasons had the movie?"]).numpy().reshape([512])
query_vector_2 = gecko_model.get_embeddings(["How many seasons had the movie?"])[0].values

#%%
# Build a ScaNN index with L2 distance metric and 10 random projection hash tables
searcher_1 = scann.scann_ops_pybind.builder(dataset, num_neighbors=10, distance_measure="squared_l2").tree(
    num_leaves=16, num_leaves_to_search=16, training_sample_size=16).score_ah(
    2, anisotropic_quantization_threshold=0.2).reorder(4).build()

searcher_2 = scann.scann_ops_pybind.builder(np.array(dataset_2), num_neighbors=10, distance_measure="squared_l2").tree(
    num_leaves=16, num_leaves_to_search=16, training_sample_size=16).score_ah(
    2, anisotropic_quantization_threshold=0.2).reorder(4).build()

# Create a directory for the serialized index
if not os.path.exists("scann_index"):
    os.makedirs("scann_index")
 
# Save the index to disk
searcher_1.serialize("scann_index")
searcher_2.serialize("scann_index")

# Load the index from disk
#searcher = scann.scann_ops_pybind.load_searcher("scann_index/")

# Generate a query vector

# Find the top 10 nearest neighbors of the query vector
k = 4
neighbors, distances = searcher_1.search(query_vector, final_num_neighbors=k)
neighbors2, distances2 = searcher_2.search(np.array(query_vector_2), final_num_neighbors=k)


# neighbours is an array of indexes for nearest neighbors. distances is an array with their corresponding squared_L2 distnaces
#%%
print(neighbors,distances)
print(neighbors2,distances2)

#%%
print(_dataset[neighbors[0]].keys())
print(__dataset[neighbors2[0]].keys())
# %%
print(_dataset[neighbors[1]].keys())
print(__dataset[neighbors2[1]].keys())