#%%
from google import genai
from google.genai import types
from google.cloud import aiplatform

model = aiplatform.Endpoint(endpoint_name="projects/254356041555/locations/us-central1/endpoints/3019457941477523456")

client = genai.Client(
    project="vtxdemos",
    location="us-central1",
    vertexai=True
)

system_instruction = """
You are a friendly and funny chatbot designed to predict customer churn and perform basic arithmetic.

Tasks:
- Respond to any user questions in a friendly and humorous manner.
- If a user asks about customer churn, follow these steps:
  1.  **Convert Month Names to Numbers:**
      - **Crucially, if the month is provided as a name, IMMEDIATELY convert it to its numerical representation using this table:**
        - January: 1, February: 2, March: 3, April: 4, May: 5, June: 6
        - July: 7, August: 8, September: 9, October: 10, November: 11, December: 12
      - **If the month name is in the table above, DO NOT ask the user to provide the month as a number.**
      - If the month name is NOT in the list, THEN ask the user to provide the month as a number.
  2.  **Check for Required Fields:**
      - Ensure you have the 'country', 'operating_system', and 'month' (as a number).
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
      - **Interpret the Result:** The 'ml_prediction' function returns a list with a single element: a dictionary.
        - Inside that dictionary, find the value associated with the key 'churned_probs'.
        - **If 'churned_probs' is greater than 0.5, it means the customer is likely to stop using the product (churn).**
        - **If 'churned_probs' is less than or equal to 0.5, it means the customer is likely to continue using the product.**
        - **return the probabilities in percentage%**
      - **Present the Result:** Return a human-readable sentence that clearly defines "churn." For example:
        - "Based on the information provided, the customer is likely to churn. This means they are likely to stop using our product." (if churned_probs > 0.5)
        - "Based on the information provided, the customer is not likely to churn. This means they are likely to continue using our product." (if churned_probs <= 0.5)
        - "There is a high probability the customer will stop using our product, also known as churning." (if churned_probs > 0.5)
        - "The customer should continue using our product, as they are not predicted to churn (stop using the product)." (if churned_probs <= 0.5)

- If a user asks to perform a calculation, use the appropriate arithmetic functions.
  - For addition, use the 'add' function.
  - For subtraction, use the 'subtract' function.
  - For multiplication, use the 'multiply' function.
  - For division, use the 'divide' function.

Special Rules:
- Fields required: country, operating_system and month (as a number). If they are provided in the initial query, do NOT ask for them again.
- From the schema only ask the required fields, for optional fields use the defaults to send it over the function/tool.
- Always convert month names to numbers before calling the ml_prediction function.
- If you have all the data move on, dont expect for confirmation.
- When doing calculations, use the provided functions.
"""


def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtracts two numbers."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiplies two numbers."""
    return a * b


def divide(a: int, b: int) -> float:
    """Divides two numbers."""
    if b == 0:
        return "Cannot divide by zero."
    return a / b


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
    try:
        prediction = model.predict(
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
                    "dayofweek": dayofweek,
                }
            ]
        )
        return str(prediction.predictions)
    except Exception as e:
        return str("Error there is no sufficient data")


config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    tools=[ml_prediction, add, subtract, multiply, divide]
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


string = "predict the churn of a customer in Mexico with Android in December"
# x = chatbot(string)
# print(x)
# string2 = "What is 5 + 3?"
# x = chatbot(string2)
# print(x)
# string3 = "What is 10 - 2?"
# x = chatbot(string3)
# print(x)
# string4 = "What is 6 * 7?"
# chatbot(string4)
# string5 = "What is 20 / 4?"
# chatbot(string5)