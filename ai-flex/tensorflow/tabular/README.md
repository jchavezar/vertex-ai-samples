![](../../images/aip-flex.png)

## Getting Started

All the steps are modular/flexible so the order is not important, variables.py is the file for setting the values.

## For custom containers
### Build & Push Images

Container Images Sizes:
cpu = 2.45GB
gpu = 12.3GB

```sh
docker build -t us-central1-docker.pkg.dev/vtxdemos/custom-trains/tf-preprocess_cpu:1.0 -f trainer/Dockerfile\[CPU\] trainer/.
docker push us-central1-docker.pkg.dev/vtxdemos/custom-trains/tf-preprocess_cpu:1.0

docker build -t us-central1-docker.pkg.dev/vtxdemos/custom-trains/tf-preprocess_gpu:1.0 -f trainer/Dockerfile\[GPU\] trainer/.
docker push us-central1-docker.pkg.dev/vtxdemos/custom-trains/tf-preprocess_gpu:1.0
```

## For pre-built containers
### Build Eggs or Python Distribution Packages and Copy to GCS
```sh
python setup.py sdist --formats=gztar
gsutil cp dist/trainer-0.1.tar.gz gs://vtxdemos-dist/ai-flex-train/trainer-0.1.tar.gz
```