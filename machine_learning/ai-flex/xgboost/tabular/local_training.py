#%%

#region Import Libraries
import os
import logging
import argparse
import xgboost as xgb
from google.cloud import bigquery
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
#endregion

def main(args):
    #region Preparing dataset
    #From bigquery dataset to pandas dataframe
    #dataset="vtxdemos.public.wholesale_customers_data"
    #client = bigquery.Client(os.getenv("CLOUD_ML_PROJECT_ID", "vtxdemos"))
    #df = client.query(f"SELECT * FROM `{args.dataset_dir}`").to_dataframe()
    import pandas as pd
    train = pd.read_csv("train.csv")
    test = pd.read_csv("test.csv")
    train['target'].replace(["Class_1", "Class_2", "Class_3", "Class_4"], [0,1,2,3], inplace=True)
    train.drop(columns=['id'])
    test.drop(columns=['id'])
    
    train.to_csv("train_2.csv", index=False)
    
    #Splitting dataframe
    X = train.iloc[:,:-1]
    # Dependant variable
    y = train['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0)

    #endregion

    #region Training
    # We need to define parameters as dict

    # Training
    print(("=========== Start Trial: [] ============="))
    model_xgb = xgb.XGBClassifier(
        n_estimators = 180,
        random_state=1,
         use_label_encoder=True,
        learning_rate = args.learning_rate,
        max_depth = args.max_depth,
        gamma = args.gamma,
        reg_alpha = args.reg_alpha,
        colsample_bytree = args.colsample_bytree
        )
     
    xgb_params = {}
    xgb_params['eval_metric'] = 'auc'
    xgb_params['early_stopping_rounds'] = 50 
    model_xgb.set_params(**xgb_params)
    model_xgb.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], verbose=True)
    print(f"Best iteration: {model_xgb.best_iteration}")
    #endregion
    
    pred = model_xgb.predict_proba(X_test)
    print(y_test)
    print(pred)
    _roc_auc_score = roc_auc_score(y_test, pred, multi_class="ovr")
    logging.info(f"Evaluation completed with model accuracy: {_roc_auc_score}")
    print(_roc_auc_score)
    #region Hyperparameter-Tuning
    if args.hypertune:
        from hypertune import HyperTune
        
        pred = model_xgb.predict(X_test)
        _roc_auc_score = roc_auc_score(y_test, pred>0.5)
        logging.info(f"Evaluation completed with model accuracy: {_roc_auc_score}")

        hpt = HyperTune()
        hpt.report_hyperparameter_tuning_metric(
        hyperparameter_metric_tag = 'roc_auc_score',
        metric_value = _roc_auc_score,
        global_step = 1)
    #endregion
        
    #region Storing Model in GCS    
    gs_prefix = 'gs://'
    gcsfuse_prefix = '/gcs/'
    if args.model_dir.startswith(gs_prefix):
        args.model_dir = args.model_dir.replace(gs_prefix, gcsfuse_prefix)
        dirpath = os.path.split(args.model_dir)[0]
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
    gcs_model_path = os.path.join(args.model_dir, 'model.json')    
    model_xgb.save_model(gcs_model_path)
    
    #model2 = xgb.XGBRegressor()
    #model2.load_model(args.model_file)
    #endregion
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_dir",
                        type=str, 
                        help="bigquery dataset project_id.dataset.table",
                        default="vtxdemos.public.wholesale_customers_data"
                        )
    parser.add_argument("--learning_rate",
                        type=float, 
                        help="learning rate",
                        default=0.01
                        )
    parser.add_argument("--max_depth",
                        type=int, 
                        help="max_depth",
                        default=3
                        )
    parser.add_argument("--model_dir",
                        type=str, 
                        help="model location and filename",
                        default=os.getenv('AIP_MODEL_DIR')
                        )
    parser.add_argument('--gamma',
                    default=1, type=int,
                    help='Tree gamma.')
    parser.add_argument('--reg_alpha',
                    default=1, type=int,
                    help='Alpha Reg.')
    parser.add_argument('--colsample_bytree',
                    default=0.5, type=float,
                    help='Colum sample tree depth.')    
    parser.add_argument("--hypertune",
                        type=bool, 
                        help="hyperparameter tune",
                        default=False
                        )
    args = parser.parse_args()
    
    main(args)
    
# %%
