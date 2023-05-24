
import os
import argparse
from ai.vertex import bq_load, train

parser = argparse.ArgumentParser()
parser.add_argument("--train_data", help="Name of the training dataset in format bq: project.dataset.table")
parser.add_argument("--eval_data", help="Name of the evaluation dataset in format bq: project.dataset.table")
args = parser.parse_args()

## BigQuery Omni Loading Data from AWS
train_df, eval_df = bq_load(args.train_data, args.eval_data)
train(train_df, eval_df)
