import os
import json
import dask
import argparse
import subprocess
import dask_bigquery
import xgboost as xgb
from google.cloud import storage
from xgboost import dask as dxgb
from dask.distributed import Client
from dask_cuda import LocalCUDACluster
import warnings
warnings.filterwarnings(action="ignore")

class Training:
    def __init__(self, project, bq_table_dir, num_workers, threads_per_worker):
        self.project = project
        self.bq_table_dir = bq_table_dir
        self.num_workers = num_workers
        self.threads_per_worker = threads_per_worker
        
        print(self.threads_per_worker)
    
    def load_data(self):
        '''Load data from BigQuery to Dask'''
        _ = self.bq_table_dir.split('.')
    
        ddf = dask_bigquery.read_gbq(
            project_id='jchavezar-demo',
            dataset_id=_[0],
            table_id=_[1]
        ).dropna()
        
        print(f"[INFO] ------ Splitting dataset")
        df_train, df_eval = ddf.random_split([0.8, 0.2], random_state=123)
        self.df_train_features = df_train.drop('Cover_Type', axis=1)
        self.df_eval_features = df_eval.drop('Cover_Type', axis=1)
        self.df_train_labels = df_train.pop('Cover_Type')
        self.df_eval_labels = df_eval.pop('Cover_Type')
    
    def model_train(self):
        print("[INFO] ------ Creating dask cluster")
        scheduler_ip = subprocess.check_output(['hostname','--all-ip-addresses'])
        scheduler_ip = scheduler_ip.decode('UTF-8').split()[0]
        
        with LocalCUDACluster(
            ip=scheduler_ip,
            n_workers=self.num_workers, 
            threads_per_worker=self.threads_per_worker
        ) as cluster:
            with Client(cluster) as client:
                print('[INFO]: ------ Calling main function ')

                print("[INFO]: ------ Dataset for dask")
                dtrain = dxgb.DaskDeviceQuantileDMatrix(client, self.df_train_features, self.df_train_labels)
                dvalid = dxgb.DaskDeviceQuantileDMatrix(client, self.df_eval_features, self.df_eval_labels)

                print("[INFO]: ------ Training...")
                output = xgb.dask.train(
                    client,
                    {
                        "verbosity": 2, 
                        "tree_method": "gpu_hist", 
                        "objective": "multi:softprob",
                        "eval_metric": ["mlogloss"],
                        "learning_rate": 0.1,
                        "gamma": 0.9,
                        "subsample": 0.5,
                        "max_depth": 9,
                        "num_class": 8
                    },
                    dtrain,
                    num_boost_round=10,
                    evals=[(dvalid, "valid1")],
                    early_stopping_rounds=5
                )
                model = output["booster"]
                best_model = model[: model.best_iteration]
                print(f"[INFO] ------ Best model: {best_model}")
                best_model.save_model("/tmp/model.json")
                model_metrics = output["history"]["valid1"]
                with open("/tmp/metadata.json", "w") as outfile:
                    json.dump(model_metrics, outfile)
    
    def storage_artifacts(self):        
        print('[INFO] ------ Storing Artifacts on Google Cloud Storage')
        bucket = os.environ['AIP_MODEL_DIR'].split('/')[2]
        blob_name = '/'.join(os.environ['AIP_MODEL_DIR'].split('/')[3:])
        bucket ='vtx-models'
        storage_client = storage.Client(project=self.project)
        bucket = storage_client.bucket(bucket)

        for i in ["model.json", "metadata.json"]:
            blob = bucket.blob(f'{blob_name}{i}')
            blob.upload_from_filename(f'/tmp/{i}')        
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--project',
        type = str,
        default = os.environ['CLOUD_ML_PROJECT_ID'],
        help = 'This is the tenant or the Google Cloud project id name'
    )
    parser.add_argument(
        "--bq_table_dir",
        type = str,
        help = "BigQuery Dataset URI in the format [DATASET].[TABLE]"
    )
    parser.add_argument(
        '--num_workers', type=int, help='num of workers',
        default=1
    )
    parser.add_argument(
        '--threads_per_worker', type=int, help='num of threads per worker',
        default=1
    )
    
    args = parser.parse_args()
    training = Training(args.project, args.bq_table_dir, args.num_workers, args.threads_per_worker)
    training.load_data()
    training.model_train()
    training.storage_artifacts()
