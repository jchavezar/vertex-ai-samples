#%%
import pandas as pd
from pytorch_tabular import TabularModel
from pytorch_tabular.models import CategoryEmbeddingModelConfig
from pytorch_tabular.config import DataConfig, OptimizerConfig, TrainerConfig, ExperimentConfig
from pytorch_tabular.models.common.heads import LinearHeadConfig

train = pd.read_csv('gs://vtx-datasets-public/pytorch_tabular/synthetic/train.csv')
test = pd.read_csv('gs://vtx-datasets-public/pytorch_tabular/synthetic/test.csv')
val = pd.read_csv('gs://vtx-datasets-public/pytorch_tabular/synthetic/val.csv')

cat_col_names = [col for col in train.columns if 'cat' in col]
num_col_names = [col for col in train.columns if 'num' in col]

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
tabular_model.save_model('tabular_random_model')
# %%
tabular_model.predict(test)
# %%

inst = [-0.13958516956070632,
 -1.3606400530352043,
 0.0,
 3.0,
 3.0,
 -3.499027938224948,
 1.5616820431786256,
 0.9539908208453985,
 0.4393174224127471,
 1.243787826881755,
 0.07209993596721286,
 0.6012383169168973,
 0.7183716353698507,
 0.16496191147994038,
 -2.726836288836686,
 0.944248100479719,
 0.8211842730812101,
 0.36864743007076256,
 0.0,
 0.12632291869729445]

columns = ['num_col_0','num_col_1','cat_col_2','cat_col_3','cat_col_4','num_col_5',
'num_col_6','num_col_7','num_col_8','num_col_9','num_col_10','num_col_11','num_col_12','num_col_13',
'num_col_14','num_col_15','num_col_16','num_col_17','cat_col_18','num_col_19']

data_pred = pd.DataFrame([inst],columns=columns)
# %%
tabular_model.predict(data_pred)


# %%
