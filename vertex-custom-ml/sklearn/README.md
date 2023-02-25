How to?

**run.py** will have all the code required to do training on vertex and deploy a prediction container with the model generated, we first need to create the containers for training and prediction.

## Create the Training Image and run run.py

- go to [training folder](./training) and run the following command:

***gcloud builds will generate a docker image and push it in the repo specified***

```bash
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/sklearn-train .
```

## Create the Prediction Image and run run.py

- go to [prediction folder](./prediction) and run the following command:

```bash
# %%
gcloud builds submit -t gcr.io/{YOUR_PROJECT_ID}/ecommerce:fast-onnx .
```

## Deploy for online predictions

<table align="left">
  <td>
    <a href="https://colab.research.google.com/github/jchavezar/vertex-ai-samples/blob/main/vertex-custom-ml/pytorch/custom_jobs/pypackage_from_local_tabclass.ipynb">
      <img src="https://cloud.google.com/ml-engine/images/colab-logo-32px.png" alt="Colab logo"> Run in Colab
    </a>
  </td>
</table>

Happy coding!
