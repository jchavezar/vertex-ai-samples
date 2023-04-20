#%%
import os
import json
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from google.cloud import bigquery
import tensorflow_datasets as tfds
callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)

print("Version: ", tf.__version__)
print("Eager mode: ", tf.executing_eagerly())
print("Hub version: ", hub.__version__)
print("GPU is", "available" if tf.config.list_physical_devices('GPU') else "NOT AVAILABLE")

client = bigquery.Client(project="vtxdemos")

## Loading testing dataset from bigquery
sql = "select * from `public.train_nlp`"
train_df = client.query(sql).to_dataframe()
train_examples = np.array([i.encode('utf-8') for i in train_df['text']], dtype="object")
train_labels = train_df['labels'].to_numpy(dtype=int)

## Load pre-trained model (BERT)
model = "https://tfhub.dev/google/nnlm-en-dim50/2"
hub_layer = hub.KerasLayer(model, input_shape=[], dtype=tf.string, trainable=True)

## Splitting datasets
x_val = train_examples[:10000]
partial_x_train = train_examples[10000:]

y_val = train_labels[:10000]
partial_y_train = train_labels[10000:]

## Create new nn layers
model = tf.keras.Sequential()
model.add(hub_layer)
model.add(tf.keras.layers.Dense(16, activation='relu'))
model.add(tf.keras.layers.Dense(1))

model.compile(optimizer='adam',
              loss=tf.losses.BinaryCrossentropy(from_logits=True),
              metrics=[tf.metrics.BinaryAccuracy(threshold=0.0, name='accuracy')])

#%%
history = model.fit(partial_x_train,
                    partial_y_train,
                    epochs=20,
                    batch_size=512,
                    validation_data=(x_val, y_val),
                    verbose=1,
                    callbacks=[callback])
model.save(os.getenv('AIP_MODEL_DIR'))

with open('/gcs/vtxdemos-models/nlp/history.json', 'w') as f:
    json.dump(history.history, f)
