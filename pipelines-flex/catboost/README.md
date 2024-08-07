# Vertex Pipelines Custom Training
The following guide explores different ways to create kubeflow components from the ground by using 
[Container Components](https://www.kubeflow.org/docs/components/pipelines/user-guides/components/container-components/#a-simple-container-component).


### Prerequisites
Create Training Container Image

```mermaid
flowchart TB
    AA((can change)) --> A
    A(train.py) --> B(kubeflow component)
    B --> C(kfp/vertex pipelines)
    C --> D((Managed Service))
    C --> E((Google Kubernetes))
    F(inference.py) --> G(docker/unicorn)
    G --> I(deploy.py) --> J(kubeflow component)
    J --> K(kfp/vertex pipelines)
    K --> D
    K --> E

```

```bash
gcloud builds submit --config cloudbuild.yaml
```

Run Pipeline
```bash
python pipeline_run.py
```