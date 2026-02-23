from google.cloud import discoveryengine_v1alpha as discoveryengine

project_number = "254356041555"
engine_id = "agentspace-testing_1748446185255"

client = discoveryengine.ConversationalSearchServiceClient()
session_path = client.session_path(
    project=project_number,
    location="global",
    collection="default_collection",
    data_store=engine_id, # Wait, is engine_id a data_store or engine?
    session="-"
)
print("Session path:", session_path)
