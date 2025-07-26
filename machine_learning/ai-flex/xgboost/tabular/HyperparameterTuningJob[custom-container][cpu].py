#%%
from variables import *
from google.cloud import aiplatform
from google.cloud.aiplatform import hyperparameter_tuning as hpt

aiplatform.init(project=project_id, location=region, staging_bucket=staging_bucket)

#region vertexai CustomJob
job = aiplatform.CustomJob(
    display_name=display_name_job+"-cpu",
    worker_pool_specs=[
        {
            "machine_spec": {
                "machine_type": machine_type_cpu,
                #"accelerator_type": accelerator_type,
                #"accelerator_count": accelerator_count,
            },
            "replica_count": replica_count,
            "container_spec": {
                "image_uri": custom_train_image_uri_cpu,
                "args": [
                    "python", 
                    "-m", 
                    "trainer.train", 
                    "--dataset_dir", 
                    dataset_dir,
                    "--hypertune",
                    "True"
                    ]
            },
        },
    ],
    labels= {
        "ai-flex": "hcustom-train-wholesales-cpu"
        },
    base_output_dir=model_dir
)
#endregion

hp_job = aiplatform.HyperparameterTuningJob(
    display_name='hp-test',
    custom_job=job,
    metric_spec={
        'roc_auc_score': 'maximize',
    },
    parameter_spec={
        'learning_rate': hpt.DoubleParameterSpec(min=0.001, max=0.1, scale='log'),
        'max_depth': hpt.IntegerParameterSpec(min=3, max=128, scale='linear'),
        "gamma": hpt.IntegerParameterSpec(min=1, max=9, scale="linear"),
        "reg_alpha": hpt.IntegerParameterSpec(min=1, max=9, scale="linear"),
        "colsample_bytree": hpt.DoubleParameterSpec(min=0.5, max=1, scale="log"),
    },
    max_trial_count=4,
    parallel_trial_count=4,
    labels={'ai-flex': 'hcustom-train-wholesales-cpu'},
    )

hp_job.run()
# %%
#region print the best

best = (None, None, None, 0.0)
for trial in hp_job.trials:
    # Keep track of the best outcome
    if float(trial.final_measurement.metrics[0].value) > best[3]:
        try:
            best = (
                trial.id,
                float(trial.parameters[0].value),
                float(trial.parameters[1].value),
                float(trial.final_measurement.metrics[0].value),
            )
        except:
            best = (
                trial.id,
                float(trial.parameters[0].value),
                None,
                float(trial.final_measurement.metrics[0].value),
            )

print(best)
best_mod = best[0]
#endregion
# %%
!gsutil ls $model_dir$best_mod/model
# %%
