#%%
import pandas as pd
import argparse
import os

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_selection import SelectPercentile, chi2
from sklearn.linear_model import LogisticRegression
from google.cloud import storage
import warnings
warnings.filterwarnings('ignore')

if __name__ == "__main__":
    # Loading Training Data
    print('--- [INFO] Data loading...')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_dir',
        default='gs://vtx-datasets-public/ecommerce', 
        type=str, 
        help='A Cloud storage URI for saving datasets')
    parser.add_argument(
        '--model_dir',
        default=os.environ['AIP_MODEL_DIR'], 
        type=str, 
        help='A Cloud storage URI for saving datasets')
    args = parser.parse_args()

    # Variables
    MODEL_DIR = args.model_dir
    BUCKET_NAME = MODEL_DIR.split('/')[2]
    BUCKET_SUFFIX_NAME = '/'.join(MODEL_DIR.split('/')[2:])
    MODEL_FILENAME = 'ecommerce.onnx'
    DATA_DIR = args.data_dir
    
    train_df = pd.read_csv(f'{DATA_DIR}/train.csv')
    test_df = pd.read_csv(f'{DATA_DIR}/test.csv')
    val_df = pd.read_csv(f'{DATA_DIR}/val.csv')

    # Create features and labels
    labels = 'will_buy_on_return_visit'
    y_train = train_df[labels]
    x_train = train_df.drop([labels], axis=1)
    y_val = val_df[labels]
    x_val = val_df.drop([labels], axis=1)
    num_cols = [i for i in x_train.columns if x_train[i].dtypes == 'int64']
    cat_cols = [i for i in x_train.columns if x_train[i].dtypes == 'object']

    #%%
    # Create pipeline transformation and training
    print('--- [INFO] Transformation pipeline creation')
    numeric_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")),("scaler", StandardScaler())]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ("selector", SelectPercentile(chi2, percentile=50))
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_cols),
            ("cat", categorical_transformer, cat_cols)
        ]
    )

    clf = Pipeline(
        steps=[("preprocessor", preprocessor),("classifier", LogisticRegression())]
    )
    print('--- [INFO] Training job started')
    clf.fit(x_train, y_train)

    # %%
    # Convert into ONNX format
    print('--- [INFO] Training job finished')
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import Int64TensorType, StringTensorType
    schema = []
    for col, col_type in zip(x_train.columns, x_train.dtypes):
        if col_type == "object":
            schema_type = StringTensorType([None, 1])
        else:
            schema_type = Int64TensorType([None, 1])
        schema.append((col, schema_type))

    onx = convert_sklearn(clf, initial_types=schema)
    with open("/tmp/ecommerce.onnx", "wb") as f:
        f.write(onx.SerializeToString())

    # Store model in Google Cloud Storage
    print(f'--- [INFO] Storing Model:{MODEL_FILENAME} has been started')
    print(BUCKET_NAME)
    print(BUCKET_SUFFIX_NAME)
    print(f'{BUCKET_SUFFIX_NAME}/{MODEL_FILENAME}')
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    object = bucket.blob(f'{BUCKET_SUFFIX_NAME}/{MODEL_FILENAME}')
    object.upload_from_filename('/tmp/ecommerce.onnx')
    print(f'--- [INFO] object has been stored in gs://{BUCKET_NAME}/{BUCKET_SUFFIX_NAME}')