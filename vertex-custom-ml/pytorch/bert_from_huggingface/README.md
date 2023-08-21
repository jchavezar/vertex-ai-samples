# Bert Uncased Huggingface
Context: Step by step to upload [bert uncased](https://huggingface.co/bert-base-uncased) model from Huggingface for inference.

## Prerequisites

[Vertex AI Endpoints](https://cloud.google.com/vertex-ai/docs/general/deployment) is a managed service to deploy models from another managed service called [Model Registry](https://cloud.google.com/vertex-ai/docs/model-registry/introduction) which keeps versioning of the code.

To use the service we have to load the model into a web server container, in the next example we use FastAPI but we can also use Flask or any other web server.

This folder contains 3 files:
- **Dockerfile**: Contains the image with all the libraries required by the model.
- **main.py**: Contains the code where the model is uploaded and deployed.
- **bert_uncased_custom_end.py**: Contains the code to:
    - Build and Push docker image.
    - Import the docker image into Model Registry.
    - Create/List Endpoint:
    - Deploy image version in Model Registry into Endpoint.

The configuration looks like this:

## Loading Model 
```
app = FastAPI()

unmasker = pipeline('fill-mask', model='bert-base-uncased')
unmasker("Hello I'm a [MASK] model.")
```
## Webserver Config

```
@app.get('/health_check')
def health():
    return 200
if os.environ.get('AIP_PREDICT_ROUTE') is not None:
    method = os.environ['AIP_PREDICT_ROUTE']
else:
    method = '/predict'
    
@app.post(method)
async def predict(request: Request):
    print("----------------- PREDICTING -----------------")
    body = await request.json()
    output=unmasker(body["instances"])
    return JSONResponse({"predictions": output})
```
.