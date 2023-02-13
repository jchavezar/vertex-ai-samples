[Feast](https://feast.dev/) is a standalone, open-source feature store that organizations use to store and serve features consistently for offline training and online inference.
The next script is to create the infrastructure behind [feature servers](https://docs.feast.dev/reference/feature-servers).

## Prerequisites

* *Install Google SDK please see [documentation](https://cloud.google.com/sdk/docs/install)
* *Install docker, please see [documentation](https://docs.docker.com/engine/install/ubuntu/)

## Building Docker Image

Teraform will help to create the infrastructure underneath feast-servers, the components created by Terraform are google kubernetes cluster, redis memorystore and the credentials to authenticate services.

### Create Dockerfile (declarative file to build containers)
```commandline
FROM python:3.9

RUN pip install feast
RUN feast init feature_repo
WORKDIR /feature_repo/feature_repo
RUN feast apply
RUN feast materialize-incremental $(date +%Y-%m-%d)

EXPOSE 6566

CMD ["feast", "serve"]
```

### Authenticate to push/pull Images from GCP

*[google cloud sdk need to be installed]*

```commandline
gcloud auth configure-docker
```

### Build Docker Image (locally)
```commandline
docker build -t gcr.io/**[your project]**/feast:v1 .
```

### Push to Google Cloud Repository
```commandline
docker push gcr.io/**[your project]**/feast:v1
```