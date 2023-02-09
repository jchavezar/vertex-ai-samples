
import pandas as pd
import argparse
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

parser = argparse.ArgumentParser()
parser.add_argument('--epochs', dest='epochs',
                    default=10, type=int,
                    help='Number of epochs.')
parser.add_argument('--num_units', dest='num_units',
                    default=64, type=int,
                    help='Number of unit for first layer.')
args = parser.parse_args()

col_names = ["Length", "Diameter", "Height", "Whole weight", "Shucked weight", "Viscera weight", "Shell weight", "Age"]
target = "Age"

def aip_data_to_dataframe(wild_card_path):
    return pd.concat([pd.read_csv(fp.numpy().decode(), names=col_names)
                      for fp in tf.data.Dataset.list_files([wild_card_path])])

def get_features_and_labels(df):
    return df.drop(target, axis=1).values, df[target].values

def data_prep(wild_card_path):
    return get_features_and_labels(aip_data_to_dataframe(wild_card_path))


model = tf.keras.Sequential([layers.Dense(args.num_units), layers.Dense(1)])
model.compile(loss='mse', optimizer='adam')

model.fit(*data_prep(os.environ["AIP_TRAINING_DATA_URI"]),
          epochs=args.epochs ,
          validation_data=data_prep(os.environ["AIP_VALIDATION_DATA_URI"]))
print(model.evaluate(*data_prep(os.environ["AIP_TEST_DATA_URI"])))

# save as Vertex AI Managed model
tf.saved_model.save(model, os.environ["AIP_MODEL_DIR"])
