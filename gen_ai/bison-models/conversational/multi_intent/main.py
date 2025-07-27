import gradio as gr
from utils.google_tools import llm

client = llm()

intents = []
chat_history = []

def greet(prompt):
    intent = client.chat_intent_detection(prompt)
    print(intent)
    intents.append(intent)
    print(intents)
    if intents[0] == "default_intent" and len(intents)==1:
        print("1")
        res = client.chat_conversation(intents[0], chat_history=chat_history)
    elif intents[-2] == "default_intent" and intents[-1] == "default_intent":
        print("2")
        res = client.chat_conversation(intents[0], chat_history=chat_history)
        chat_history.append({"intent_type": intents[0], "human": prompt, "bot": res})
    elif intents[-2] != "default_intent" and intents[-1] == "default_intent":
        print("3")
        res = client.chat_conversation(intents[-2], chat_history=chat_history)
        chat_history.append({"intent_type": intents[-2], "human": prompt, "bot": res})
        print("4")
    elif intents[-2] != "default_intent" and intents[-1] != "default_intent":
        res = client.chat_conversation(intents[-1], chat_history=chat_history)
        chat_history.append({"intent_type": intents[-1], "human": prompt, "bot": res})
    elif intents[-2] == "default_intent" and intents[-1] != "default_intent":
        res = client.chat_conversation(intents[-1], chat_history=chat_history)
        chat_history.append({"intent_type": intents[-1], "human": prompt, "bot": res})
    return res

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
    
if __name__ == "__main__":
    demo.launch(show_api=False)   