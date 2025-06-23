from google.adk.agents import Agent
from google import genai

client = genai.Client(
    vertexai=True,
    project="vtxdemos",
    location="us-central1"
)

def comparator(ocr: str):
    """
    You are a tool comparator, which compares source data (data_to_compare) against data read from the orchestrator
    (root_agent) model.
    :param ocr:
    :return:
    """
    data_to_compare = "Receipt Number: 123, Data Paid: March 23, 2024."
    re = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[f"""your mission is to compare this data {ocr}, from this data_to_compare: {data_to_compare},
        only compare data that matches.
        
        Give me a summary of your comparisons, do not give me code.
        """]
    )
    return re.text

root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash-001",
    description="You are a AI Comparator Assistant.",
    instruction="""
    Follow only the following tasks:
    * ** Detect the Intent **
    Based on the intent:
    - If its a general question just answer directly.
    - If you have the keyword COMPARE or similar continue with
    the next instructions:
    1. Extract the information from the pdf as text.
    2. Pass the text to your tool `comparator`
    3. Give me the response from comparator.
    """,
    tools=[comparator]
)