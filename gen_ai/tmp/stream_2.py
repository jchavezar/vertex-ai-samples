import time
import streamlit as st
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models


# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def llm_predict(question: str):
    config = {
        "max_output_tokens": 2048,
        "temperature": 0.9,
        "top_p": 1
    }
    model = GenerativeModel("gemini-1.0-pro-001")
    chat = model.start_chat()
    res = chat.send_message(f"{question}", generation_config=config, safety_settings={
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    })

    # noinspection PyBroadException
    try:
        re = res.text
    except:
        re = res

    return re

def generate_response(user_query):
    context = "".join(st.session_state['chat_history'])  # Build context from history
    result = llm_predict(question=user_query)
    return result

def main():
    st.title("Multi-Turn Q&A Chatbot")

    # Display chat history
    for message in st.session_state['chat_history']:
        if message.startswith('User:'):
            st.info(message)  # User messages
        else:
            st.success(message)  # Bot messages

    user_input = st.text_input("Ask me something:")

    if user_input:
        with st.spinner("Thinking..."):
            response = generate_response(user_input)

            # Typing effect
            for word in response.split(" "):
                st.write_stream(word + " ")
                time.sleep(0.1)

            # Update chat history
            st.session_state['chat_history'].append("User: " + user_input)
            st.session_state['chat_history'].append("Bot: " + response)

if __name__ == "__main__":
    main()
