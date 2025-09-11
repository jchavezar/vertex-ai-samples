#%%
from google import genai

project_id="vtxdemos"
region="us-central1"
model_id="gemini-2.5-flash"

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=region,
)

def get_completion(
        prompt: str,
):
    try:
        re = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                thinking_config=genai.types.ThinkingConfig(
                    thinking_budget=0
                )
            )
        )
        return re.text
    except Exception as e:
        return f"There was an error: {e}"


def prompt_chain(_initial_prompt, _follow_up_prompts):
    result = get_completion(_initial_prompt)
    if result is None:
        return "Initial prompt failed."
    print(f"Initial output: {result}\n")
    for i, prompt in enumerate(_follow_up_prompts, 1):
        full_prompt = f"{prompt}\n\nPrevious output: {result}"
        result = get_completion(full_prompt)
        if result is None:
            return f"Prompt {i} failed."
        print(f"Step {i} output: {result}\n")
    return result

initial_prompt = "Summarize the key trends in global temperature changes over the past century."
follow_up_prompts = [
    "Based on the trends identified, list the major scientific studies that discuss the causes of these changes.",
    "Summarize the findings of the listed studies, focusing on the impact of climate change on marine ecosystems.",
    "Propose three strategies to mitigate the impact of climate change on marine ecosystems based on the summarized findings."
]
final_result = prompt_chain(initial_prompt, follow_up_prompts)
print("Final result:", final_result)