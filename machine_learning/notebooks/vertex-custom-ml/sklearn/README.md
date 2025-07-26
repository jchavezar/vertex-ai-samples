
<a href="https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform"><img src="https://img.shields.io/badge/aiplatform-1.22.0-blue"/></a>


## Key Features

- In code

* [**scikit-learn**](https://scikit-learn.org/stable/); free software machine learning library to transform, train and evaluate.
* [**google-cloud-storage**](https://cloud.google.com/storage/docs/reference/libraries); RESTful online file storage web serving to store objects.
* [**onnx**](https://onnx.ai/); is an open format built to represent machine learning models
* [**FastAPI**](https://fastapi.tiangolo.com/); is a modern, fast (high-performance), web framework for building APIs with Python 3.7+.
 
 - Out code

 * [**vertex/aiplatform**](https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform); a machine learning (ML) platform that lets you train and deploy ML models and AI applications.

## How To Use 

There are different ways to have training-predictions on Vertex; using containers, local-python-file, python distribution package, [run.py](run.py) has all the steps to fire training and predictions using those different ways, some of them need docker container images so let's build them first:

## Create the Training Image

- go to [training folder](training) and run the following command:

*the following snippet creates a docker image and push it into a repository, remember to use {YOUR_PROJECT_ID}*

```bash
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/sklearn-train .
```

## Create the Prediction Image

- go to [prediction folder](prediction) and run the following command:

```bash
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/ecommerce:fast-onnx .
```

## Fire up! Use [run.py](run.py)

*Remember to change variables*

## or use Notebooks:

- [container/customJob](container.ipynb)


Happy coding!
