## BQ_Omni
## Follow steps as showed here: https://cloud.google.com/bigquery/docs/omni-aws-create-connection
## Create Policy and Role in AWS
## Create a Connection from BQ using the role created before
## Change identity id in AWS
## Create Dataset
## Create Table from S3 bucket with csv file


## Testing connection with bq_omni
#%%
from google.cloud.bigquery import Client
client = Client(project="vtxdemos")
query = """
SELECT * FROM `vtxdemos.bq_omni_demo.train_dataset`
"""
df = client.query(query).to_dataframe()

# %%

import pandas as pd
from pytorch_tabular import TabularModel
from pytorch_tabular.models import CategoryEmbeddingModelConfig
from pytorch_tabular.config import DataConfig, OptimizerConfig, TrainerConfig, ExperimentConfig
from pytorch_tabular.models.common.heads import LinearHeadConfig

cat_col_names = ["os", "country", "is_mobile"]
num_col_names = ["pageviews"]

data_config = DataConfig(
    target=['label'], #target should always be a list. Multi-targets are only supported for regression. Multi-Task Classification is not implemented
    continuous_cols=num_col_names,
    categorical_cols=cat_col_names,
)

trainer_config = TrainerConfig(
    auto_lr_find=True, # Runs the LRFinder to automatically derive a learning rate
    batch_size=1024,
    max_epochs=20,
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

tabular_model.fit(train=df)
# %%

eval_df = pd.read_csv("eval_dataset.csv")
eval_df.head()
# %%
from sklearn.metrics import accuracy_score, f1_score
result = tabular_model.evaluate(eval_df)

#%%
pred = tabular_model.predict(eval_df)

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

print_metrics(eval_df['label'], pred["prediction"], tag="Holdout")

# %%
