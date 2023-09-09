#%%
import os
import warnings
import argparse
import tensorflow as tf
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')

df = pd.read_csv("gs://vtxdemos-datasets-public/ecommerce/train.csv")
train_df, val_df, test_df = np.split(df.sample(frac=1, random_state=42), [int(.6*len(df)), int(.8*len(df))]) 
df = train_df.copy()
labels = df.pop('will_buy_on_return_visit')
df = {key: np.array(value)[:, None] for key, value in train_df.items()}
ds = tf.data.Dataset.from_tensor_slices((dict(df), labels))

#%%
ds = ds.batch(254).prefetch(254)
# %%
