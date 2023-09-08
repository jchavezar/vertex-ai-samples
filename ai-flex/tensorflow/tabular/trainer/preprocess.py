import os
import time
import numpy as np
import pandas as pd
import tensorflow as tf

class Client:        
    def transform(self, 
                  dataset: str, 
                  gcp: bool, 
                  aws: bool, 
                  azure: bool):

        if gcp:
            df = pd.read_csv(dataset)
            
        elif aws:
            df = pd.read_csv(
                dataset,
                storage_options={
                    "key": os.environ["AWS_ACCESS_KEY_ID"],
                    "secret": os.environ["AWS_SECRET_ACCESS_KEY"],
                    },
                )

        ### Shuffling and Splitting ###
        train_df, val_df, test_df = np.split(df.sample(frac=1, random_state=42), [int(.6*len(df)), int(.8*len(df))]) 
        
        ################################### PREPROCESSING ######################################## Convert pandas dataframe to tensor data (from GCS to TF.data.Datainit_start = time.process_time(def df_to_dataset(dataframe)    df = dataframe.copy(    labels = df.pop('will_buy_on_return_visit'    df = {key: np.array(value)[:, None] for key, value in dataframe.items()    ds = tf.data.Dataset.from_tensor_slices((dict(df), labels)    ds = ds.batch(batch_size).prefetch(batch_size    return ds
        
        ## Convert pandas dataframe to tensor data (from GCS to TF.data.Data)
        init_start = time.process_time()
        def df_to_dataset(dataframe):
            df = dataframe.copy()
            labels = df.pop('will_buy_on_return_visit')
            df = {key: np.array(value)[:, None] for key, value in dataframe.items()}
            ds = tf.data.Dataset.from_tensor_slices((dict(df), labels))
            ds = ds.batch(batch_size).prefetch(batch_size)
            return ds        

        ## Normalization / Standarization
        def get_normalization_layer(name, dataset):
            start = time.process_time()
            normalizer = tf.keras.layers.Normalization(axis=None)
            feature_ds = dataset.map(lambda x, y: x[name])
            normalizer.adapt(feature_ds)
            print(f'Normalization time for {name}: {time.process_time() - start}')
            return normalizer
        
        # Performs feature-wise categorical encoding of inputs features
        def get_category_encoding_layer(name, dataset, dtype, max_tokens=None):
            start = time.process_time()
            if dtype == 'string':
                index = tf.keras.layers.StringLookup(max_tokens=max_tokens)
            else:
                index = tf.keras.layers.IntegerLookup(max_tokens=max_tokens)
            feature_ds = dataset.map(lambda x, y: x[name])
            index.adapt(feature_ds)
            encoder = tf.keras.layers.CategoryEncoding(num_tokens=index.vocabulary_size())
            print(f'Encoding time for {name}: {time.process_time() - start}')
            return lambda feature: encoder(index(feature))

        batch_size = 256
        train_ds = df_to_dataset(train_df)
        val_ds = df_to_dataset(val_df)
        test_ds = df_to_dataset(test_df)

        ## Identify Numerical and Categorical columns:
        num_columns = ['latest_ecommerce_progress', 'time_on_site', 'pageviews']
        cat_columns = ['source', 'medium', 'channel_grouping', 'device_category', 'country']
        num_cat_columns = 'bounces'

        all_inputs = []
        encoded_features = []

        # Numerical Features.
        for header in num_columns:
            numeric_col = tf.keras.Input(shape=(1,), name=header)
            normalization_layer = get_normalization_layer(header, train_ds)
            encoded_numeric_col = normalization_layer(numeric_col)
            all_inputs.append(numeric_col)
            encoded_features.append(encoded_numeric_col)

        # Categorical Features.
        for header in cat_columns:
            categorical_col = tf.keras.Input(shape=(1,), name=header, dtype='string')
            encoding_layer = get_category_encoding_layer(name=header,
                                                         dataset=train_ds,
                                                         dtype='string',
                                                         max_tokens=5)
            encoded_categorical_col = encoding_layer(categorical_col)
            all_inputs.append(categorical_col)
            encoded_features.append(encoded_categorical_col)

        ## Integer values into integer indices.
        bounces_col = tf.keras.Input(shape=(1,), name=num_cat_columns, dtype='int64')

        encoding_layer = get_category_encoding_layer(name=num_cat_columns,
                                                     dataset=train_ds,
                                                     dtype='int64',
                                                     max_tokens=5)
        encoded_age_col = encoding_layer(bounces_col)
        all_inputs.append(bounces_col)
        encoded_features.append(encoded_age_col)

        print(f'Total preprocessing time: {time.process_time() - init_start}')
        
        return train_ds, val_ds, test_ds, encoded_features, all_inputs

        #########################################################################################