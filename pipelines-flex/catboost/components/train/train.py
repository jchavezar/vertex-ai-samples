import argparse
import logging
import numpy as np
from google.cloud import bigquery, aiplatform, storage
from catboost import CatBoostClassifier, Pool, metrics, cv
import os
import tempfile

def upload_to_gcs(local_file, gcs_path):
  client = storage.Client()
  bucket_name, blob_path = gcs_path.replace("/gcs/", "").split("/", 1)
  bucket = client.bucket(bucket_name)
  blob = bucket.blob(blob_path)
  blob.upload_from_filename(local_file)

def train(bq_dataset, project_id, output_file, run_num):
  bq_client = bigquery.Client(project=project_id)
  train_ratio = 0.7
  test_ratio = 0.1

  query = f"""
    WITH data AS (
      SELECT *, RAND() AS random_value
      FROM `{bq_dataset}`
    )
    
    SELECT *, 
      CASE 
        WHEN random_value < {train_ratio} THEN 'train'
        WHEN random_value >= {train_ratio} AND random_value < {train_ratio + test_ratio} THEN 'test'
        ELSE 'val' 
      END AS split_set
    FROM data
    """

  df = bq_client.query(query).to_dataframe()
  train_df = df[df['split_set'] == 'train'].copy()
  test_df = df[df['split_set'] == 'test'].copy()
  val_df = df[df['split_set'] == 'val'].copy()
  train_df.drop(['split_set', 'random_value'], axis=1, inplace=True)
  test_df.drop(['split_set', 'random_value'], axis=1, inplace=True)
  val_df.drop(['split_set', 'random_value'], axis=1, inplace=True)
  train_x = train_df.drop('will_buy_on_return_visit', axis=1)
  train_y = train_df.will_buy_on_return_visit
  test_x = test_df.drop('will_buy_on_return_visit', axis=1)
  test_y = test_df.will_buy_on_return_visit
  val_x = val_df.drop('will_buy_on_return_visit', axis=1)
  val_y = val_df.will_buy_on_return_visit
  categorical_features_indices = np.where(train_x.dtypes != float)[0]

  model = CatBoostClassifier(
      allow_writing_files=False,
      train_dir="/tmp",
      custom_loss=[metrics.Accuracy()],
      random_seed=42,
  )

  model.fit(
      train_x, train_y,
      cat_features=categorical_features_indices,
      eval_set=(val_x, val_y),
  )

  cv_params = model.get_params()
  cv_params.update({'loss_function': metrics.Logloss()})
  cv_data = cv(Pool(train_x, train_y, cat_features=categorical_features_indices), cv_params)
  accuracy_score = np.max(cv_data['test-Accuracy-mean'])
  std_score = cv_data['test-Accuracy-std'][np.argmax(cv_data['test-Accuracy-mean'])]
  step = np.argmax(cv_data['test-Accuracy-mean'])

  print(f'Best validation accuracy score: {accuracy_score:.2f}±{std_score:.2f} on step {step}')

  predictions = model.predict(test_x)
  predictions_probs = model.predict_proba(test_x)
  print(predictions[:10])
  print(predictions_probs[:10])

  aiplatform.start_run(run_num)
  aiplatform.log_params({"accuracy_score": str(accuracy_score), "std_score": str(std_score), "step": str(step)})

  # Save the model to a temporary local file
  with tempfile.TemporaryDirectory() as tmpdirname:
    local_model_path = os.path.join(tmpdirname, "model.json")
    model.save_model(local_model_path, format="json", export_parameters=None, pool=None)

    # Upload the local file to GCS
    gcs_output_path = os.path.join(output_file, "model.json")
    upload_to_gcs(local_model_path, gcs_output_path)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Catboost Training')
  parser.add_argument("--bq-dataset", type=str, default="vtxdemos.demos_us.ecommerce_balanced")
  parser.add_argument("--project-id", type=str, default="vtxdemos")
  parser.add_argument("--experiment-name", type=str, default="catboost-ecommerce")
  parser.add_argument("--run-num", type=str)
  parser.add_argument("--output-file", type=str, default="/gcs/vtxdemos-staging/model")
  args = parser.parse_args()

  aiplatform.init(experiment=args.experiment_name, experiment_tensorboard=False, project=args.project_id, location="us-central1")
  train(bq_dataset=args.bq_dataset, project_id=args.project_id, output_file=args.output_file, run_num=args.run_num)
