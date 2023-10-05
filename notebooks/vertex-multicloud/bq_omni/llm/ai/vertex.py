import pandas as pd
import os

project_id = os.environ["CLOUD_ML_PROJECT_ID"]

def bq_load(train_dataset: str, eval_dataset):
    import os
    from google.cloud.bigquery import Client
    client = Client(project=project_id)
    return client.query(f"""SELECT * FROM `{train_dataset}`""").to_dataframe(), client.query(f"""SELECT * FROM `{eval_dataset}`""").to_dataframe()

def create_eval_table(pred_dataset: pd.DataFrame):
    import os
    from google.cloud import bigquery
    client = bigquery.Client(project=project_id)
    job = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(pred_dataset, f"{project_id}.public.pred_data")
    job.result()
    
    
def train(train_dataset: pd.DataFrame, eval_dataset: pd.DataFrame):    
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

    tabular_model.fit(train=train_dataset)
    pred = tabular_model.predict(eval_dataset)
    create_eval_table(pred)
    
    return tabular_model
