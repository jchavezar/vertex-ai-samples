#%%
import json

from google import genai
from google.genai import types
from google.cloud import modelarmor_v1

project = "jesusarguelles-sandbox"
location = "us-central1"

client = modelarmor_v1.ModelArmorClient(transport="rest", client_options = {"api_endpoint" : "modelarmor.us.rep.googleapis.com"})
gemini_client = genai.Client(
    vertexai=True,
    project=project,
    location=location
)

def intercept_message(prompt: str) -> str:
    user_prompt_data = modelarmor_v1.DataItem()
    user_prompt_data.text = prompt
    request = modelarmor_v1.SanitizeUserPromptRequest(
        name="projects/jesusarguelles-sandbox/locations/us/templates/ssn-test",
        user_prompt_data=user_prompt_data,
    )
    response = client.sanitize_user_prompt(request=request)

    print(response)
    print(response.sanitization_result.filter_results["sdp"].sdp_filter_result.inspect_result.match_state.name)

    if response.sanitization_result.filter_results["sdp"].sdp_filter_result.inspect_result.match_state.name == "MATCH_FOUND":
        block_prompt = "yes"
        reason = response.sanitization_result.filter_results["sdp"].sdp_filter_result.inspect_result.match_state.name
        byte_start = response.sanitization_result.filter_results["sdp"].sdp_filter_result.inspect_result.findings[0].location.byte_range.start
        sdp_detected = prompt[byte_start:]
        info_type = response.sanitization_result.filter_results["sdp"].sdp_filter_result.inspect_result.findings[0].info_type
        prompt = prompt[:byte_start]
    else:
        block_prompt = "no"
        reason = "na"
        sp_detected = "non"
        info_type = "non"
        prompt = prompt

    system_instruction = """
    Your an AI assistant to answer any question, you pass through a validation using
    a model armor method which masks the private information, if something like that is
    receive it just mention that you cant expose the private information.
    
    In the output give the original prompt masking the private data with the info_type.
    
    ## e.g.
    
    Hi my name is Jesus Chavez
    
    I'm sorry I can't process any private information.
    
    Your original query:
    Hi my [NAME_LAST_NAME] is XXXXXXX
    ## end of e.g.
    """

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
    )

    part = types.Part.from_text(text=f"""
    block_prompt: {block_prompt},
    reason: {reason},
    info_type: {info_type},
    prompt: {prompt}
    """)

    re = gemini_client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[part],
        config=config
    )
    return re.text

x=intercept_message("My social is 123-45-7890, can you if theres any information on internet?")
print(x)


#%%
from ai_model_armor import extract_matches
from google.cloud import modelarmor_v1

client = modelarmor_v1.ModelArmorClient(transport="rest", client_options = {"api_endpoint" : "modelarmor.us.rep.googleapis.com"})

user_prompt_data = modelarmor_v1.DataItem()
user_prompt_data.text = "super fuck you!"
request = modelarmor_v1.SanitizeUserPromptRequest(
    name="projects/jesusarguelles-sandbox/locations/us/templates/ai-template",
    user_prompt_data=user_prompt_data,
)
response = client.sanitize_user_prompt(request=request)
print(response.sanitization_result.filter_results["rai"].rai_filter_result.match_state.name)

if response.sanitization_result.filter_results["rai"].rai_filter_result.match_state.name == "MATCH_FOUND":
    print("-")
    for k,v in response.sanitization_result.filter_results["rai"].rai_filter_result.rai_filter_type_results.items():
        print(k)
        print(v)


#%%
import json

# Assuming 'response' is your actual Protobuf response object
# Let's get to the map we are interested in:
source_map = response.sanitization_result.filter_results["rai"].rai_filter_result.rai_filter_type_results

output_dict = {}

for key, value_message in source_map.items():
    details = {}

    # Extract match_state (appears to be always present)
    # Assumes value_message.match_state is an enum object with a .name attribute
    if hasattr(value_message, 'match_state') and hasattr(value_message.match_state, 'name'):
        details['match_state'] = value_message.match_state.name
    else:
        # Fallback or error handling if the structure is different than expected
        details['match_state'] = 'UNKNOWN'


    # Extract confidence_level if it's present and not the default/unspecified value
    # Assumes value_message.confidence_level is an enum object with .name and .value attributes,
    # and that an enum value of 0 means it's "unspecified" and should be omitted.
    if hasattr(value_message, 'confidence_level'):
        confidence_obj = value_message.confidence_level
        if hasattr(confidence_obj, 'value') and hasattr(confidence_obj, 'name'):
            if confidence_obj.value != 0:  # Only include if not the default (0) enum value
                details['confidence_level'] = confidence_obj.name
        # If confidence_level might be an attribute that is None when not set
        elif confidence_obj is not None and hasattr(confidence_obj, 'name'):
            # This case might apply if it's an optional message field rather than an enum defaulting to 0
            # For enums, the .value != 0 check is usually more accurate for proto3
            details['confidence_level'] = confidence_obj.name


    output_dict[key] = details

# Convert the dictionary to a JSON string
json_output = json.dumps(output_dict, indent=2)

# Print the resulting JSON
print(json_output)