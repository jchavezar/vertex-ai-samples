import csv
import random
import itertools
from ai import LLM
import streamlit as st
from collections import Counter
from google.cloud import firestore

db=firestore.Client(project="vtxdemos")

#@st.cache_data
def q_a(base_info):
    def create_dictionary():
        ## Create dictionary from datastore
        bios = {}
        for i in range(98):
            docs = db.collection(f"bios_{i}").stream()
            _dict = {}
            for doc in docs:
                _dict[doc.id] = doc.to_dict()
            bios[f"bios_{i}"]=_dict
        # Aggregating questions
        for v in bios.values():
            for k,v in v.items():
                if k == "skills":
                    v["question"] = "What are your skills?"
        return bios

    stored_dictionary = create_dictionary()

    freq_q = []
    for v in stored_dictionary.values():
        for k,v in v.items():
            if k != "original_text" and "experience" not in k and "occupation" not in k not in base_info:
                freq_q.append(v["question"])
    fre_q_d=dict(sorted(dict(Counter(freq_q)).items(), key=lambda x:x[1], reverse=True))
    top5_q=list(dict(itertools.islice(fre_q_d.items(), 3)).keys())
    print(top5_q)

    _dict={}
    for i in top5_q:
        _list=[]
        for k1,v1 in stored_dictionary.items():
            for k2,v2 in v1.items():
                if k2 != "original_text":
                    if i == v2["question"]:
                        _list.append(v2["answer"])
        _list = [x for x in _list if x != ""]
        _dict[i] = list(set(_list))

    return _dict

def random_strong_bios_pick():
    ## Create dictionary from datastore
    strong_bios = []
    for i in range(98):
        docs = db.collection(f"bios_{i}").stream()
        for doc in docs:
            if doc.id == "original_text":
                strong_bios.append(doc.to_dict()["text"])
    return random.choice(strong_bios)