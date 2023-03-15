## This is not a notebook, I use vscode with python extension and run ipykernel with individual cells
#%% 
PROJECT_ID = 'jchavezar-demo'
TRAIN_IMAGE = 'gcr.io/jchavezar-demo/pytorch-custom-random:v1'
STAGING_BUCKET = 'gs://vtx-staging'

#%%

!rm -fr source
!mkdir source

#%%
%%writefile source/train.py
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import random
import numpy as np
import pandas as pd
import os
# %load_ext autoreload
# %autoreload 2

def make_mixed_classification(n_samples, n_features, n_categories):
    X,y = make_classification(n_samples=n_samples, n_features=n_features, random_state=42, n_informative=5)
    cat_cols = random.choices(list(range(X.shape[-1])),k=n_categories)
    num_cols = [i for i in range(X.shape[-1]) if i not in cat_cols]
    for col in cat_cols:
        X[:,col] = pd.qcut(X[:,col], q=4).codes.astype(int)
    col_names = [] 
    num_col_names=[]
    cat_col_names=[]
    for i in range(X.shape[-1]):
        if i in cat_cols:
            col_names.append(f"cat_col_{i}")
            cat_col_names.append(f"cat_col_{i}")
        if i in num_cols:
            col_names.append(f"num_col_{i}")
            num_col_names.append(f"num_col_{i}")
    X = pd.DataFrame(X, columns=col_names)
    y = pd.Series(y, name="target")
    data = X.join(y)
    return data, cat_col_names, num_col_names

def print_metrics(y_true, y_pred, tag):
    if isinstance(y_true, pd.DataFrame) or isinstance(y_true, pd.Series):
        y_true = y_true.values
    if isinstance(y_pred, pd.DataFrame) or isinstance(y_pred, pd.Series):
        y_pred = y_pred.values
    if y_true.ndim>1:
        y_true=y_true.ravel()
    if y_pred.ndim>1:
        y_pred=y_pred.ravel()
    val_acc = accuracy_score(y_true, y_pred)
    val_f1 = f1_score(y_true, y_pred)
    print(f"{tag} Acc: {val_acc} | {tag} F1: {val_f1}")


data, cat_col_names, num_col_names = make_mixed_classification(n_samples=10000, n_features=20, n_categories=4)
train, test = train_test_split(data, random_state=42)
train, val = train_test_split(train, random_state=42)
path = os.path.join('/gcs/vtx-datasets-public', 'synthetic_data')
os.mkdir(path)
test.to_csv(f'{path}/test.csv')

from pytorch_tabular import TabularModel
from pytorch_tabular.models import CategoryEmbeddingModelConfig
from pytorch_tabular.config import DataConfig, OptimizerConfig, TrainerConfig, ExperimentConfig
from pytorch_tabular.models.common.heads import LinearHeadConfig

data_config = DataConfig(
    target=['target'], #target should always be a list. Multi-targets are only supported for regression. Multi-Task Classification is not implemented
    continuous_cols=num_col_names,
    categorical_cols=cat_col_names,
)
trainer_config = TrainerConfig(
    auto_lr_find=True, # Runs the LRFinder to automatically derive a learning rate
    batch_size=1024,
    max_epochs=100,
    accelerator="auto", # can be 'cpu','gpu', 'tpu', or 'ipu' 
)
optimizer_config = OptimizerConfig()


head_config = LinearHeadConfig(
    layers="", # No additional layer in head, just a mapping layer to output_dim
    dropout=0.1,
    initialization="kaiming"
).__dict__ # Convert to dict to pass to the model config (OmegaConf doesn't accept objects)

model_config = CategoryEmbeddingModelConfig(
    task="classification",
    layers="32-16", # Number of nodes in each layer
    activation="LeakyReLU", # Activation between each layers
    dropout=0.1,
    initialization="kaiming",
    head = "LinearHead", #Linear Head
    head_config = head_config, # Linear Head Config
    learning_rate = 1e-3
)


tabular_model = TabularModel(
    data_config=data_config,
    model_config=model_config,
    optimizer_config=optimizer_config,
    trainer_config=trainer_config,
)

tabular_model.fit(train=train, validation=val)
tabular_model.save_model('/gcs/vtx-models/pytorch/tabular_random')

# %%
%%writefile source/Dockerfile
FROM python:3.10.10-slim-bullseye

COPY . .

RUN pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113 
RUN pip install pytorch_tabular[extra]

ENTRYPOINT ["python", "train.py"]

# %%
!docker build -t $TRAIN_IMAGE source/.
!docker push $TRAIN_IMAGE

# %%
!rm -fr source

#%%

## Using Vertex AI to Train Custom Model (managed service)
### Class used: aiplatform.CustomJob, version: 1.22.1
from google.cloud import aiplatform

aiplatform.init(project=PROJECT_ID, staging_bucket=STAGING_BUCKET)

worker_pool_specs = [
        {
            "machine_spec": {
                "machine_type": "n1-standard-4",
                "accelerator_type": "NVIDIA_TESLA_T4",
                "accelerator_count": 1,
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": TRAIN_IMAGE,
                "command": [],
                "args": [],
            },
        }
    ]

my_job = aiplatform.CustomJob(
    display_name='pytorch_tabular_custom',
    worker_pool_specs=worker_pool_specs,
)

my_job.run()

## Testing locally
# %%
!gsutil cp -r gs://vtx-models/pytorch/tabular_random .

## Using a GCE VM with T4 and PyTorch libraries for Testing
# %%
from pytorch_tabular import TabularModel

loaded_model = TabularModel.load_from_checkpoint("tabular_random")


# %%
