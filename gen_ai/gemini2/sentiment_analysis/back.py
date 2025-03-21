#%%
import json
from google import genai
from google.genai import types

project = "vtxdemos"
region = "us-central1"

client = genai.Client(
    vertexai=True,
    project=project,
    location=region
)

system_instructions = """
Analyze the following text for sentiment, going beyond positive, negative, and neutral. Identify the specific sentiment 
for different aspects of the product mentioned. Extract the key adjectives used and their sentiment. Determine the 
overall emotion expressed. Identify the user's intent. If there are comparisons made to other products, please highlight 
them. Also, identify the main themes discussed and the sentiment associated with each theme. Be sure to account for 
any negation or sarcasm.

Output in JSON with the following keys:
overall_emotion_expressed: String
user_intent: List<String>
sentiment_analysis_by_aspect: List<Dict<key:value>>
key_adjectives_w_sentiment: List<Dict<key:value>>
comparison_to_other_products: List<Dict<key:value>>
themes_and_sentiment: List<Dict<key:value>>
negation_and_sarcasm: List<Dict<key:value>>
summary: String
"""

config = types.GenerateContentConfig(
    system_instruction=system_instructions,
    response_mime_type="application/json"
)


def conversation_bot(prompt: str) -> str:
    try:
        re = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt,
            config=config
        )
        return re.text
    except Exception as e:
        print(f"There was an error: {e}")
        return "Error"

# prompt = ("The new phone has a stunning display, which I absolutely love! However, the battery life is terrible, "
#           "it barely lasts a few hours. The camera is okay, nothing special. Compared to its predecessor, this model "
#           "feels much slower. I'm not exactly thrilled with the purchase, to put it mildly (hint: I'm very "
#           "disappointed). The user interface is also quite confusing. Overall, it looks great but fails in "
#           "performance.")


#%%
# sentiment_counts = {}
#
# aggregated_sentiment_counts = {}
#
# # Aggregate sentiment from sentiment_analysis_by_aspect
# aspect_positive = 0
# aspect_negative = 0
# for item in re['sentiment_analysis_by_aspect']:
#     if item['sentiment'] == 'Positive':
#         aspect_positive += 1
#     elif item['sentiment'] == 'Negative':
#         aspect_negative += 1
# aggregated_sentiment_counts['sentiment_analysis_by_aspect'] = {'Positive': aspect_positive, 'Negative': aspect_negative}
#
# # Aggregate sentiment from key_adjectives_w_sentiment
# adjectives_positive = 0
# adjectives_negative = 0
# for item in re['key_adjectives_w_sentiment']:
#     if item['sentiment'] == 'Positive':
#         adjectives_positive += 1
#     elif item['sentiment'] == 'Negative':
#         adjectives_negative += 1
# aggregated_sentiment_counts['key_adjectives_w_sentiment'] = {'Positive': adjectives_positive, 'Negative': adjectives_negative}
#
# # Aggregate sentiment from themes_and_sentiment
# themes_positive = 0
# themes_negative = 0
# for item in re['themes_and_sentiment']:
#     if item['sentiment'] == 'Positive':
#         themes_positive += 1
#     elif item['sentiment'] == 'Negative':
#         themes_negative += 1
# aggregated_sentiment_counts["themes_and_sentiment"] = {'Positive': themes_positive, 'Negative': themes_negative}
#
# #%%
# print("Aggregated Sentiment Counts for Dashboards:")
# for key, counts in aggregated_sentiment_counts.items():
#     print(f"\n--- {key} ---")
#     print(f"Positive: {counts['Positive']}")
#     print(f"Negative: {counts['Negative']}")