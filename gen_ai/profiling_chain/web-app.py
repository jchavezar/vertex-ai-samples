#%%
import re
from collections import Counter
import streamlit as st
import pandas as pd
import numpy as np
from gen import ai

ai = ai()

st.title('Create your profile!')

#@st.cache_data
def basic_info():
    name = st.text_input(
        label="What's your name?",
        placeholder="name",
    )

    genre = st.text_input(
        label="Genre",
        placeholder="male",
    )

    age = st.text_input(
        label="What's your age?",
        placeholder="age",
    )

    languages = st.text_input(
       label="List your languages:",
       placeholder="English"
    )


    return {'name': name, 'age': age, 'genre': genre, 'language': languages}

base_info = basic_info()

st.text(f"Hi {base_info['name']}!, wait a sec while load important libraries...")

@st.cache_data
def llm_stage_1():
    df = pd.read_csv("strong_bios.csv", names=["strong_bios"])
    ##st.dataframe(df)

    # LLM1 -> Creating attributes from strong bios

    att_dict = {}
    pred_dict = {}
    for index, row in df.iterrows():
      att_dict[f"att_{index}"]=row["strong_bios"]
      pred_dict[f"att_{index}"]=  ai.get_attritbutes(text=row["strong_bios"])

    # Ranking attributes, Top 5 attributes:
    data = [i for k,v in pred_dict.items() for i in v]
    sorted_data = dict(sorted(dict(Counter(data)).items(), key=lambda x:x[1], reverse=True))
    top5_attributes = list(dict(list(sorted_data.items())[:5]).keys())
    return att_dict, pred_dict, top5_attributes
att_dict, pred_dict, top5_attributes = llm_stage_1()

selected_attributes = st.multiselect(
        "Match attributes?", top5_attributes, [top5_attributes[4]],
    )
attributes_user_input = st.text_input(
        label="Show more attributes:",
        placeholder="playful",
    )
collect_attributes = lambda x : [i.strip() for i in re.split(r",", x) if i != ""]
collected_attributes = collect_attributes(attributes_user_input)
attributes = selected_attributes+collected_attributes
st.write(f"These are your attributes:\n {attributes}")

#questions = ai.get_questions_for_gatter_att(top5_attributes)
#question = questions[0]
#st.write(question)
#q1 = st.text_input(label=question)
st.text_input(label="whats your philosophy of care?")
# %%

# LLM3 -> Creating profiles from attribues and strong bios

#@st.cache_data
def llm_stage_3():
    # Ranking based on all attributes selected
    _res = {}
    for k,v in pred_dict.items():
       _res[k]=sum(i in attributes for i in v)

    original_bios_info = {}
    res = dict(sorted(_res.items(), key=lambda x:x[1], reverse=True))
    for n,i in enumerate(res.keys()):
       original_bios_info[i]={"scoring": res[i], "strong_bio": att_dict[i], "attributes": pred_dict[i]}

    # 1 original dictionary with all items and top 3 strong_bios for samples
    bios_info=original_bios_info
    bios_info=dict(list(bios_info.items())[:3])    
    generated_bios = {}

    for n,i in enumerate(bios_info):
      gen_bios=ai.get_profiles(basic_info=base_info,strong_bio=bios_info[i]["strong_bio"], attributes=attributes)
      generated_bios[f"generated_bio_{n+1}"]=gen_bios

    return bios_info, generated_bios

bios_info, generated_bios = llm_stage_3()

for (k1,v1), (k2,v2) in zip(bios_info.items(), generated_bios.items()):
    count=+0
    st.markdown("**:blue[[STRONG_BIO]]**:\n")
    st.write(f"[STRONG BIO]:\n")
    st.write(f"{bios_info[k1]['strong_bio']}\n")
    st.markdown("**:red[[GENERATED_BIO]]**:\n")
    st.write(generated_bios[k2])
    st.write("--"*120+"\n")


### Questions to enhance bios:

for (k1,v1), (k2,v2) in zip(generated_bios.items(),bios_info.items()):
   q=ai.get_questions_for_gatter_att_2(generated_bios[k1],bios_info[k2]['strong_bio'])

st.write(q)