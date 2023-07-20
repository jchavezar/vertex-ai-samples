#%%
import random
import yaml
import itertools
from ai import LLM
from utils import q_a, random_strong_bios_pick
import streamlit as st
from collections import Counter
from google.cloud import firestore
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

ai = LLM()
db=firestore.Client(project="vtxdemos")
llm_response = ""


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

    st.title('Create your profile!')
    
    with st.form(key='basic_info'):
        #@st.cache_data
        def basic_info():
            name = st.text_input(
                label="What's your name?",
                placeholder="name",
            )

            languages = st.text_input(
            label="What languages do you speak?",
            placeholder="English"
            )

            education_level = st.text_input(
            label="University Attended:",
            placeholder="University"
            )

            number_of_years_of_experience = st.text_input(
            label="Years of Experience:",
            placeholder="# years"
            )

            cpr_trained = st.radio(
            "CPR Trained?",
            options=["yes", "no"], index=1)

            first_aid_trained = st.radio(
            "First Aid Trained?",
            options=["yes", "no"], index=1)

            special_needs_children = st.radio(
            "Works with special needs children",
            options=["yes", "no"], index=1)

            child_development_coursework = st.radio(
            "Has Early Child Development Coursework",
            options=["yes", "no"], index=1)

            early_childhood_edu = st.radio(
            "Has Early Childhood Education",
            options=["yes", "no"], index=1)

            comfortable_with_pets = st.radio(
            "Are you comfortable with pets?",
            options=["yes", "no"], index=1),

            if cpr_trained == "no":
                cpr_trained="I'm not CPR trainer"
            else: "I'm CPR trainer"

            if first_aid_trained == "no":
                first_aid_trained="I'm not First Aid trained"
            else: "I'm First Aid trained"

            return {
                'name': name, 
                'language': languages, 
                'education_level': education_level, 
                'number_of_years_of_experience': number_of_years_of_experience,
                'cpr_trained': cpr_trained,
                'first_aid_trained': first_aid_trained,
                'special_needs_children': special_needs_children,
                'child_development_coursework': child_development_coursework,
                'early_childhood_edu': early_childhood_edu,
                'comfortable_with_pets': comfortable_with_pets,
                }

        base_info = basic_info()
        submit_form = st.form_submit_button('Enter')

    #with st.form(key='llm_info'):
    #    text = st.text_input('text')
    #    st.form_submit_button('Enter')

    @st.cache_data
    def gen_ai(text):
        return ai.extract_topics(text)

    if True:

        form = base_info
        #@st.cache_data
        def setting_up_environment():
            q_a_dict = q_a(base_info)
            top5_q=list(q_a_dict.keys())

            if "random_answers" not in st.session_state:
                qa = {}
                for n,v in enumerate(q_a_dict.values()):
                    qa[n]=random.choice(v)
                st.session_state["random_answers"] = qa
            else: pass
            #random_answers={}
            
            return top5_q, st.session_state["random_answers"]
        
        top5_q, random_answers = setting_up_environment()

        st.write(form)
        
        def clear_form():
            st.session_state[top5_q[0]]=""
            st.session_state[top5_q[1]]=""
            st.session_state[top5_q[2]]=""
        
        def clear_form2():
            st.session_state["newq1"]=""
            st.session_state["newq2"]=""

        bio_strong_text_template=random_strong_bios_pick()

        if all(x != "" for x in form.values()):
            with st.form(key="bios_1_form"):
                form["info0"] = st.text_input(top5_q[0], key=top5_q[0], placeholder=st.session_state["random_answers"][0])
                form["info1"] = st.text_input(top5_q[1], key=top5_q[1], placeholder=st.session_state["random_answers"][1])
                form["info2"] = st.text_input(top5_q[2], key=top5_q[2], placeholder=st.session_state["random_answers"][2])
                #form["info3"] = st.text_input(top5_q[3], key=top5_q[3], placeholder=st.session_state["random_answers"][3])
                #form["info4"] = st.text_input(top5_q[4], key=top5_q[4], placeholder=st.session_state["random_answers"][4])
                submit_button = st.form_submit_button(label='Submit')
                clear = st.form_submit_button(label="Clear", on_click=clear_form)
            st.write(form)
            #st.write(f"Strong Bios Template Used:\n {bio_strong_text_template}")
            bio = ai.create_profile(form, bio_strong_text_template)
            #st.write(bio)

            if all(x != "" for x in form.values()):
                add_q = ai.additional_questions(bio, top5_q)
                #st.write(f"Bios Generated by LLM:\n {bio}")

                if "new_questions" not in st.session_state:
                    st.session_state["new_questions"] = {n:q for n,q in enumerate(add_q.keys())}
                if "new_answers" not in st.session_state:
                    st.session_state["new_answers"] = {n:a for n,a in enumerate(add_q.values())}

                with st.form(key="bios_2_form"):
                    #st.write(st.session_state["new_questions"])
                    form["additional_question_1"] = st.text_input(st.session_state["new_questions"][0], key="newq1", placeholder=st.session_state["new_answers"][0])
                    form["additional_question_2"] = st.text_input(st.session_state["new_questions"][1], key="newq2", placeholder=st.session_state["new_answers"][1])
                    submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    st.write("Creating new profile with new questions.... \n")
                    st.write(form)
                    new_bio = ai.create_profile(form, bio_strong_text_template)
                    st.write(f"New profile:\n {new_bio}")
                    def restart(): 
                        ai.create_profile(form, random_strong_bios_pick())
                        st.write(f"New profile:\n {new_bio}")
                    st.button("Shuffle",on_click=restart)
                    st.button("Clear", on_click=clear_form)


# %%
