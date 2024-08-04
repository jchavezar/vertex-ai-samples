import os
import warnings
import argparse
import tensorflow as tf
from trainer import preprocess
from google.cloud import aiplatform
warnings.filterwarnings('ignore')

################################### ARGUMENTS ########################################

parser = argparse.ArgumentParser()
parser.add_argument(
    '--dataset', 
    help='dataset to train',
    type=str
)
parser.add_argument(
    '--run_name',
    help='name of the run',
    type=str,
)
parser.add_argument(
    '--experiment_name',
    help='name of the experiment',
    type=str,
    default="ecommerce-experiment"
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
    ################################### FEATURE ENGINEERING #################################

    # aiplatform.init(experiment=args.experiment_name, project=os.environ["CLOUD_ML_PROJECT_ID"])
    # aiplatform.start_run(run=args.run_name)

    client = preprocess.Client()
    train_ds, val_ds, test_ds, encoded_features, all_inputs = client.transform(
        dataset=args.dataset,
        gcp=args.gcp,
        aws=args.aws,
        azure=args.azure
        )
    
    print("test")
    print(encoded_features)

    ################################### CREATE, COMPILE AND TRAIN MODEL #####################

    all_features = tf.keras.layers.concatenate(encoded_features)
    x = tf.keras.layers.Dense(32, activation="relu")(all_features)
    x = tf.keras.layers.Dropout(0.5)(x)
    output = tf.keras.layers.Dense(1)(x)

    model = tf.keras.Model(all_inputs, output)

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                  metrics=[
                      tf.keras.metrics.BinaryAccuracy(name='accuracy'),
                      tf.keras.metrics.Precision(name='precision'),
                      tf.keras.metrics.Recall(name='recall'),
                      tf.keras.metrics.AUC(name='auc'),
                      tf.keras.metrics.AUC(name='prc', curve='PR'),
                  ])
    print('compile pass')
    ################################## SETUP TENSORBOARD LOGS AND TRAIN #####################

    print(os.environ['AIP_TENSORBOARD_LOG_DIR'])
    print('---------------------')
    print(os.environ['AIP_MODEL_DIR'])

    #tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=os.environ['AIP_TENSORBOARD_LOG_DIR'], update_freq='batch')
    model.fit(train_ds, epochs=15, validation_data=val_ds)
    loss, accuracy, precision, recall, auc, prc = model.evaluate(test_ds)
    print("Loss:", loss)
    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("AUC:", auc)
    print("PRC:", prc)

    # aiplatform.log_metrics(
    #     {
    #         "loss": loss,
    #         "accuracy": accuracy,
    #         "precision": precision,
    #         "recall": recall,
    #         "auc": auc,
    #         "prc": prc,
    #      }
    # )

    ################################### SAVE MODEL ##########################################

    model.save(os.environ['AIP_MODEL_DIR'])


