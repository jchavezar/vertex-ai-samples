How to?

**run.py** will have all the code required to do training on vertex and deploy a prediction container with the model generated, we first need to create the containers for training and prediction.

## Create the Training Image and run run.py

- go to training folder and run the following command:

***gcloud builds will generate a docker image and push it in the repo specified***

```bash
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/sklearn-train .
```

## Create the Prediction Image and run run.py

- go to prediction folder and run the following command:

```bash
# %%
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/ecommerce:fast-onnx .
```

## Deploy for online predictions

Happy coding!
