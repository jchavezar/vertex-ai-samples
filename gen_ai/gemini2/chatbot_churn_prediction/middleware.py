from google import genai
from google.genai import types
from google.cloud import aiplatform

model=aiplatform.Endpoint(endpoint_name="projects/254356041555/locations/us-central1/endpoints/3019457941477523456")

client=genai.Client(
    project="vtxdemos",
    location="us-central1",
    vertexai=True
)

system_instruction="""
You are a friendly and funny chatbot designed to predict customer churn.

Tasks:
- Respond to any user questions in a friendly and humorous manner.
- If a user asks about customer churn, follow these steps:
  1.  **Extract Information:**
      - Identify the 'country', 'operating_system', and 'month' from the user's query.
      - If 'month' is provided as a name (e.g., "December"), convert it to its numerical representation (e.g., 12).
  2.  **Check for Required Fields:**
      - Ensure you have the 'country', 'operating_system', and 'month'.
      - If any of these are missing, ask the user for the missing information, one at a time.
      - If these fields are already present in the initial user query, do NOT ask for them again.
  3.  **Gather Optional Information:**
      - Use the following default values for the optional fields:
        - user_pseudo_id: "C495AAE4F1CC79CAF4335174F95ABFAC"
        - language: "en-ca"
        - cnt_user_engagement: 139
        - cnt_level_start_quickplay: 33
        - cnt_level_end_quickplay: 27
        - cnt_level_complete_quickplay: 11
        - cnt_level_reset_quickplay: 4
        - cnt_post_score: 19
        - cnt_spend_virtual_currency: 3
        - cnt_ad_reward: 0
        - cnt_challenge_a_friend: 0
        - cnt_completed_5_levels: 1
        - cnt_use_extra_steps: 3
        - julianday: 268
        - dayofweek: 3
  4.  **Call the Prediction Function:**
      - Once you have all required and optional information, call the 'ml_prediction' function with the collected values.
      - Capture churned_probs from your Function response.
  5.  **Return the Result:**
      - Return the result of the 'ml_prediction' function to the user.
      - 1 means will churn and 0 it wont churn.

Special Rules:
- Fields required: country, operating_system and month. If they are provided in the initial query, do NOT ask for them again.
- From the schema only ask the required fields, for optional fields use the defaults to send it over the function/tool.
- For Month you might receive the name of the month, convert it to a number and use it to the function/tool, e.g. December is 12.
- If you have all the data move on, dont expect for confirmation.
"""


def ml_prediction(
    user_pseudo_id: str,
    country: str,
    operating_system: str,
    language: str,
    cnt_user_engagement: int,
    cnt_level_start_quickplay: int,
    cnt_level_end_quickplay: int,
    cnt_level_complete_quickplay: int,
    cnt_level_reset_quickplay: int,
    cnt_post_score: int,
    cnt_spend_virtual_currency: int,
    cnt_ad_reward: int,
    cnt_challenge_a_friend: int,
    cnt_completed_5_levels: int,
    cnt_use_extra_steps: int,
    month: int,
    julianday: int,
    dayofweek: int,
) -> str:
  """
  A function that predicts customer churn takes all these values,
  prints them, and returns churned probabilities, churn values and predicted churns.
  """
  # print("Received values:")
  # print(f"  user_pseudo_id: {user_pseudo_id}")
  # print(f"  country: {country}")
  # print(f"  operating_system: {operating_system}")
  # print(f"  language: {language}")
  # print(f"  cnt_user_engagement: {cnt_user_engagement}")
  # print(f"  cnt_level_start_quickplay: {cnt_level_start_quickplay}")
  # print(f"  cnt_level_end_quickplay: {cnt_level_end_quickplay}")
  # print(f"  cnt_level_complete_quickplay: {cnt_level_complete_quickplay}")
  # print(f"  cnt_level_reset_quickplay: {cnt_level_reset_quickplay}")
  # print(f"  cnt_post_score: {cnt_post_score}")
  # print(f"  cnt_spend_virtual_currency: {cnt_spend_virtual_currency}")
  # print(f"  cnt_ad_reward: {cnt_ad_reward}")
  # print(f"  cnt_challenge_a_friend: {cnt_challenge_a_friend}")
  # print(f"  cnt_completed_5_levels: {cnt_completed_5_levels}")
  # print(f"  cnt_use_extra_steps: {cnt_use_extra_steps}")
  # print(f"  month: {month}")
  # print(f"  julianday: {julianday}")
  # print(f"  dayofweek: {dayofweek}")

  try:
    prediction=model.predict(
        instances=[
            {
                "user_pseudo_id": user_pseudo_id,
                "country": country,
                "operating_system": operating_system,
                "language": language,
                "cnt_user_engagement": cnt_user_engagement,
                "cnt_level_start_quickplay": cnt_level_start_quickplay,
                "cnt_level_end_quickplay": cnt_level_end_quickplay,
                "cnt_level_complete_quickplay": cnt_level_complete_quickplay,
                "cnt_level_reset_quickplay": cnt_level_reset_quickplay,
                "cnt_post_score": cnt_post_score,
                "cnt_spend_virtual_currency": cnt_spend_virtual_currency,
                "cnt_ad_reward": cnt_ad_reward,
                "cnt_challenge_a_friend": cnt_challenge_a_friend,
                "cnt_completed_5_levels": cnt_completed_5_levels,
                "cnt_use_extra_steps": cnt_use_extra_steps,
                "month": month,
                "julianday": julianday,
                "dayofweek": dayofweek
            }
        ]
    )
    return str(prediction.predictions)
  except Exception as e:
    return str("Error there is no sufficient data")


config=types.GenerateContentConfig(
    system_instruction=system_instruction,
    tools=[ml_prediction]
)

chatbot_history = []


def chatbot(text: str):
  chatbot_history.append(types.Content(role="user", parts=[types.Part.from_text(text=text)]))
  response = client.models.generate_content(
      model="gemini-2.0-flash-001",
      contents=chatbot_history,
      config=config
  )
  print("response")
  print(response)
  print("--end_response")
  chatbot_history.append(types.Content(role="model", parts=[types.Part.from_text(text=response.text)]))
  print(chatbot_history)
  return response.text

string="predict the churn of a customer in Mexico with Android in December"