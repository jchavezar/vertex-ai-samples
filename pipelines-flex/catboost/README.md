# Quick Run MLOps
The following guide explores different ways to create kubeflow components from the ground by using 
[Container Components](https://www.kubeflow.org/docs/components/pipelines/user-guides/components/container-components/#a-simple-container-component).

*Note: I'm working in an update to use jinja to modify all the variables at once.*

### Components Used
- Kubeflow V2: Pipeline Orchestration Framework.
- Vertex AI Pipelines: Managed Infrastructure Service for Kubeflow Orchestration.
- Docker: Container Images.
- Google Cloud Build.
- Artifact Registry: Model Versioning.
- Catboost: Machine Learning Model for tabular predictive tasks like regression, classification, etc...

### Diagram
```mermaid
flowchart TB
    AA((can change)) --> A
    A(train.py) --> B(kubeflow component)
    B --> C(kfp/vertex pipelines)
    C --> D((Managed Service))
    C --> E((Google Kubernetes))
    F(inference.py) --> G(docker/unicorn)
    G --> I(deploy.py) --> J(kubeflow component)
    J --> C(kfp/vertex pipelines)
```
### Instructions
Google Cloud Build will handle the docker image building and artifact registry pushing.

From your terminal run the following:
```bash
gcloud builds submit --config cloudbuild.yaml
```

Execute the pipeline definition:
```bash
python pipeline_run.py
```