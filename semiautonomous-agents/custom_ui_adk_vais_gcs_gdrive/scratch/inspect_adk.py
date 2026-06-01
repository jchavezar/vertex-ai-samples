from google.adk.models.llm_request import LlmRequest
print("LlmRequest fields:")
for field_name, field_info in LlmRequest.model_fields.items():
    print(f"  {field_name}: {field_info.annotation}")
