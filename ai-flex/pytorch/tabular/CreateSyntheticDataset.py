#draft
import random
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

DATASET_URI = "gs://vtx-datasets-public/pytorch_tabular/synthetic"

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
train.to_csv(f'{DATASET_URI}/train.csv', index=False)
test.to_csv(f'{DATASET_URI}/test.csv', index=False)
val.to_csv(f'{DATASET_URI}/val.csv', index=False)


cat_columns = [col for col in train.columns if 'cat' in col]
num_columns = [col for col in train.columns if 'num' in col]

columns_ = pd.read_csv('gs://vtx-datasets-public/pytorch_tabular/synthetic/train.csv', nrows=0).iloc[:,:-1].columns.to_list()
columns_