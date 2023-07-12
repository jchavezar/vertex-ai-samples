#%%
import yaml
import itertools
from ai import LLM
import streamlit as st
from collections import Counter
from google.cloud import firestore
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

ai = LLM()
db=firestore.Client(project="vtxdemos")
llm_response = ""

## Getting the most frequent questions out of 50 examples:
#%%
def get_most_freq_questions() -> dict:
    freq_q = []
    for i in range(50):
        doc_ref = db.collection(f"bios_{i}")
        for n in doc_ref.get():
            doc = doc_ref.document(n.id)
            freq_q.append(doc.get().to_dict()['question'])
    # %%
    fre_q_d=sorted(dict(Counter(freq_q)).items(), key=lambda x:x[1], reverse=True)
    questions = dict(fre_q_d)
    return questions

### Authentication

with open('cred.yaml') as file:
    st.session_state.config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    st.session_state.config['credentials'],
    st.session_state.config['cookie']['name'],
    st.session_state.config['cookie']['key'],
    st.session_state.config['cookie']['expiry_days'],
    st.session_state.config['preauthorized']
)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    from ai import LLM
    ai = LLM()

    st.title('Create your profile!')
    
    with st.form(key='basic_info'):
        ##@st.cache_data
        def basic_info():
            name = st.text_input(
                label="What's your name?",
                placeholder="name",
            )

            age = st.text_input(
                label="How old are you?",
                placeholder="age",
            )

            languages = st.text_input(
            label="List your languages:",
            placeholder="English"
            )
            return {'Name': name, 'Age': age, 'Languages': languages}

        base_info = basic_info()
        st.form_submit_button('Enter')

    with st.form(key='llm_info'):
        text = st.text_input('text')
        st.form_submit_button('Enter')

    @st.cache_data
    def gen_ai(text):
        return ai.extract_topics(text)

    if text:
        llm_response = gen_ai(text)
        st.write(llm_response)

    questions = []

    #if llm_response != "":
    #    topics = [i["topic"] for i in llm_response if i["topic"] not in list(base_info.keys()) ]
    #    questions = [i["question"] for i in llm_response if i["topic"] not in list(base_info.keys())]
    #    answers = [i["answer"] for i in llm_response if i["topic"] not in list(base_info.keys())]
    #    st.write(questions)

        #for i in llm_response:
        #    if i["topic"] in list(base_info.keys()):
        #        pass
        #    else:
        #        questions.append(i["question"])
    if True:

        questions=get_most_freq_questions()
        top5_q=list(dict(itertools.islice(questions.items(), 5)).keys())
        
        form = {
            "Name" : base_info["Name"],
            "Age" : base_info["Age"],
            "Languages" : base_info["Name"]
        }

        for i in range(len(top5_q)):
            form[i] = st.text_input(top5_q[i])
        ## %%

        st.write(form)

        bio = ai.create_profile(form)
        st.write(bio)
