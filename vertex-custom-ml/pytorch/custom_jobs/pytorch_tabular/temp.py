#%%
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
test.to_csv('test.csv', index=False)

#%%
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
tabular_model.save_model("saved_models")
# %%

load_tab = tabular_model.load_model("saved_models")
loaded_model = TabularModel.load_from_checkpoint("saved_models")

# %%

columns = ['num_col_0','cat_col_1','num_col_2','num_col_3','cat_col_4',
'num_col_5','cat_col_6','num_col_7','num_col_8','cat_col_9','num_col_10',
'num_col_11','num_col_12','num_col_13','num_col_14','num_col_15','num_col_16',
'num_col_17','num_col_18','num_col_19']

data = [[-0.13958516956070632,
 0.0,
 -1.207159625169817,
 2.690513673649033,
 3.0,
 -3.499027938224948,
 3.0,
 0.9539908208453985,
 0.4393174224127471,
 2.0,
 0.07209993596721286,
 0.6012383169168973,
 0.7183716353698506,
 0.16496191147994038,
 -2.726836288836686,
 0.944248100479719,
 0.8211842730812101,
 0.36864743007076256,
 -1.1991474011002978,
 0.12632291869729445]]

test_df = pd.DataFrame(data, columns=columns)
# %%

loaded_model.predict(test_df)
# %%
