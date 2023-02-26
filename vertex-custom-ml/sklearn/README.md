How to?

**run.py** will have all the code required to do training on vertex and deploy a prediction container with the model generated, we first need to create the containers for training and prediction.

## Create the Training Image

- go to [training folder](./training) and run the following command:

***gcloud builds will generate a docker image and push it in the repo specified***

```bash
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/sklearn-train .
```

## Create the Prediction Image

- go to [prediction folder](./prediction) and run the following command:

```bash
# %%
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/ecommerce:fast-onnx .
```

## Run [run.py](./run.py)

***Remember to change variables***

## or use Notebooks:

- [container/customJob](./container.ipynb)


Happy coding!
