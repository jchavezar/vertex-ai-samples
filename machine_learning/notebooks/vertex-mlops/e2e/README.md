## E2E Pipeline

* In this example I will use the most complex approach which is more flexible than any other one.

## Create Docker Images for Training Component

There are 2 ways of building images using GCP:

1. Using docker build.
2. Using google cloud build.

*Given that I have control over the virtual machine I'm using for this example and internet bandwidth is high I will prefer option 1, but the 2nd package every step at once.*

### Build and Push image into *Google Cloud Repository*:

```
make prepare_images
```

## Create pipeline compile file (pipeline.yaml) and trigger the pipeline:

```
make training-pipeline
```