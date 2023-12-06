#%%
import sys
sys.path.append("utils")
from caregiver_ai import LLM
from caregiver_utils import random_strong_bios_pick
import streamlit as st
from google.cloud import firestore
\

ai = LLM()
db=firestore.Client(project="vtxdemos")
llm_response = ""

if True:

    st.title('Caregiver Bio Profile Create')
    st.write('Model: text-bison@002')
    with st.sidebar:
        st.markdown(
            """
            Follow me on:
    
            ldap → [@jesusarguelles](https://moma.corp.google.com/person/jesusarguelles)
    
            GitHub → [jchavezar](https://github.com/jchavezar)
            
            LinkedIn → [Jesus Chavez](https://www.linkedin.com/in/jchavezar)
            
            Medium -> [jchavezar](https://medium.com/@jchavezar)
            """
        )
    st.markdown("[github repo](https://github.com/jchavezar/vertex-ai-samples/tree/main/gen_ai/pages/Caregiver_Bio_Gen[text-bison].py)")
    
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
                cpr_trained="no"
            else: "no"

            if first_aid_trained == "no":
                first_aid_trained="I'm not First Aid trained"
            else: "I'm First Aid trained"

            return {
                'name': name, 
                'language': languages, 
                'education_level': education_level, 
                'number_of_years_of_experience': number_of_years_of_experience,
                'are_you_cpr_trained': cpr_trained,
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
        bio_strong_text_template="""
        I am a compassionate and experienced caregiver with over 5 years of experience providing top-notch care to seniors. 
        I have a deep understanding of the unique needs of seniors, and I am passionate about helping them maintain their independence and quality of life.
        """
        bio = ai.create_profile(form, bio_strong_text_template)
        
        
        if all(x != "" for x in form.values()):
            add_q = ai.additional_questions(bio)

            if "new_questions" not in st.session_state or "new_answers" not in st.session_state:
                st.session_state["new_questions"] = add_q["questions"]
                st.session_state["new_answers"] = add_q["answers"]
            with st.form(key="bios_2_form"):
                form["additional_question_1"] = st.text_input(st.session_state["new_questions"][0], key="newq1", placeholder=st.session_state["new_answers"][0])
                form["additional_question_2"] = st.text_input(st.session_state["new_questions"][1], key="newq2", placeholder=st.session_state["new_answers"][1])
                submit_button = st.form_submit_button(label='Submit')
            if submit_button:
                st.write("Creating new profile with new questions.... \n")
                st.write("**Input form + questions from strong_bios + generative questions:**")
                st.write(form)
                new_bio = ai.create_profile(form, bio_strong_text_template)
                st.write(f"**Profile Template Random Picked**: {bio_strong_text_template}")
                st.write(f"**New profile**:\n {new_bio}")
                def restart(): 
                    ai.create_profile(form, random_strong_bios_pick())
                    st.write(f"**Profile Template Random Picked**: {bio_strong_text_template}")
                    st.write(f"**New profile**:\n {new_bio}")
                st.button("Shuffle",on_click=restart)

# %%
