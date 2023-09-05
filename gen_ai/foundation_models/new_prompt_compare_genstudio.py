#%%
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

def predict_large_language_model_sample(
    api_endpoint: str,
    project: str,
    endpoint_id: str,
    content: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    location: str = "us-central1",
):
  # The AI Platform services require regional API endpoints.
  client_options = {"api_endpoint": api_endpoint}
  # Initialize client that will be used to create and send requests.
  # This client only needs to be created once, and can be reused for multiple requests.
  client = aiplatform.gapic.PredictionServiceClient(
      client_options=client_options
  )
  instance_dict = {"content": content}
  instance = json_format.ParseDict(instance_dict, Value())
  instances = [instance]
  parameters_dict = {
      "temperature": temperature,
      "maxDecodeSteps": max_decode_steps,
      "topP": top_p,
      "topK": top_k,
  }
  parameters = json_format.ParseDict(parameters_dict, Value())
  endpoint = client.endpoint_path(
      project=project, location=location, endpoint=endpoint_id
  )
  response = client.predict(
      endpoint=endpoint, instances=instances, parameters=parameters
  )
  print("response")
  predictions = response.predictions
  responses = []
  for prediction in predictions:
    print(" prediction:", dict(prediction))
    responses.append(dict(prediction))

  return responses

responses = predict_large_language_model_sample("us-central1-aiplatform.googleapis.com", "cloud-large-language-models", "4511608470067216384", '''Compare DataPrep and Dataflow
| Feature | DataPrep | DataFlow |

|---|---|---|

| Purpose | Data preparation and transformation tool for adat analysits and scientists. | Data integration and transformation tool for data engineers. |
| Programming Language | No coding required. | Python, SQL, and Scala.
| Data Sources | Supports a wide range of data sources, including CSV, JSON, XML and relation databases. | Supports a wide range of data sources, including CSV, JSON, XML and relational databases. |

Compare DataPrep and Dataflow
''', 0.2, 256, 0.8, 40, "us-central1")
# %%
for i in responses:
    print(i['content'])

# %%
