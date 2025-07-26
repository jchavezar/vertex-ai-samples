import os
import argparse
import numpy as np
import pandas as pd
from pytorch_tabular import TabularModel
from pytorch_tabular.models import CategoryEmbeddingModelConfig
from pytorch_tabular.config import DataConfig, OptimizerConfig, TrainerConfig, \
  ExperimentConfig
from pytorch_tabular.models.common.heads import LinearHeadConfig

# ################################## ARGUMENTS
# #######################################

parser = argparse.ArgumentParser()
parser.add_argument(
    '--dataset',
    help='dataset to train',
    type=str
)
parser.add_argument(
    '--gcp',
    help='test to train',
    type=bool,
    default=True
)
parser.add_argument(
    '--aws',
    help='test to train',
    type=bool,
    default=False
)
parser.add_argument(
    '--azure',
    help='test to train',
    type=bool,
    default=False
)
args = parser.parse_args()
if __name__ == "__main__":
    df = pd.read_csv(args.dataset)
    train, test, val = np.split(df.sample(frac=1, random_state=42),
                              [int(.6 * len(df)), int(.8 * len(df))])

    # ################################## FEATURE ENGINEERING
    # #################################

    cat_col_names = [col for col in train.columns if 'cat' in col]
    num_col_names = [col for col in train.columns if 'num' in col]

    data_config = DataConfig(
        target=['target'],
        # target should always be a list. Multi-targets are only supported for
        # regression. Multi-Task Classification is not implemented
        continuous_cols=num_col_names,
        categorical_cols=cat_col_names,
    )
    trainer_config = TrainerConfig(
        auto_lr_find=True,
        # Runs the LRFinder to automatically derive a learning rate
        batch_size=1024,
        max_epochs=100,
        accelerator="auto",  # can be 'cpu','gpu', 'tpu', or 'ipu'
    )
    optimizer_config = OptimizerConfig()

    head_config = LinearHeadConfig(
        layers="",
        # No additional layer in head, just a mapping layer to output_dim
        dropout=0.1,
        initialization="kaiming"
    ).__dict__  # Convert to dict to pass to the model config (OmegaConf
    # doesn't accept objects)

    model_config = CategoryEmbeddingModelConfig(
        task="classification",
        layers="32-16",  # Number of nodes in each layer
        activation="LeakyReLU",  # Activation between each layers
        dropout=0.1,
        initialization="kaiming",
        head="LinearHead",  # Linear Head
        head_config=head_config,  # Linear Head Config
        learning_rate=1e-3
    )

    # ################################## CREATE, COMPILE AND TRAIN MODEL
    # #####################

    tabular_model = TabularModel(
        data_config=data_config,
        model_config=model_config,
        optimizer_config=optimizer_config,
        trainer_config=trainer_config,
    )

    tabular_model.fit(train=train, validation=val)
    model = os.environ["AIP_MODEL_DIR"]
    model = "/gcs/" + "/".join(model.split("/")[2:])
    tabular_model.save_model(model)
