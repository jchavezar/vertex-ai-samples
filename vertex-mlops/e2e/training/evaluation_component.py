## Evaluation
from kfp.dsl import component, ClassificationMetrics, Output

@component(packages_to_install=["pandas", "db-dtypes", "google-cloud-bigquery", "tensorflow", "scikit-learn"])
def evaluation(
    project_id: str,
    model_uri: str,
    metrics: Output[ClassificationMetrics]
):
    import numpy as np
    import tensorflow as tf
    from google.cloud import bigquery
    from sklearn.metrics import confusion_matrix

    client = bigquery.Client(project=project_id)
    
    ## Loading testing dataset from bigquery
    sql = "select * from `vtxdemos.public.train_nlp`"
    test_df = client.query(sql).to_dataframe()
    test_examples = np.array([i.encode('utf-8') for i in test_df['text']], dtype="object")
    test_labels = test_df['labels'].to_numpy(dtype=int)

    ## Loading the model trained
    model = tf.keras.models.load_model(f"{model_uri}/model")
    predicted_labels = model.predict(test_examples)
    predicted_labels = [1 if i > 0.5 else 0 for i in predicted_labels]
    test_labels = test_labels.tolist()

    metrics.log_confusion_matrix(
        ['positive', 'negative'],
        confusion_matrix(test_labels, predicted_labels).tolist()
    )