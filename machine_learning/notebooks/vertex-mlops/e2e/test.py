#%%

import yaml
config = yaml.safe_load(open("training/config.yaml"))
print(config['pipeline_name'])
print(config.get('pipeline_parameters', {}))

config.get('worker_pool_specs')
#%%
print(config.get("worker_pool_specs"))

# %%

text = [
    {
        'machine_spec': {
            'machine_type': 'n1-standard-8', 
            'accelerator_type': 'NVIDIA_TESLA_T4', 
            'accelerator': 1
        }, 
        'replica_count': '1', 
        'container_spec': {
            'image_uri': 'gcr.io/vtxdemos/tensorflow-gpu-nlp-pipe:v1'
        }
    }
]
worker_pool_specs = [
    {
        "machine_spec": {
            "machine_type" : "n1-standard-8",
            "accelerator_type": "NVIDIA_TESLA_T4",
            "accelerator_count": 1
        },
        "replica_count": "1",
        "container_spec": {
            "image_uri" : "test"
        }
    }
]

print(text)
# %%
worker = config["worker_pool_specs"]
print(worker[0])
# %%
