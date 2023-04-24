## E2E Pipeline

* I'm using the most complex approach which is more flexible than any other one.

### Create Docker Images for Training Component

There are 2 ways of building images using GCP:

1. Using docker build.
2. Using google cloud build.

Here I'm using the first option given translation time is faster from the virtual machine I'm using to run these scripts.

Build and Push image into Google Cloud Repository:

```
make prepare_images
```