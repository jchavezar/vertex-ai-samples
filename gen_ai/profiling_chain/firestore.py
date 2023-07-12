#%%
import csv
import itertools
from ai import LLM
from collections import Counter
from google.cloud import firestore

ai = LLM()
db=firestore.Client(project="vtxdemos")
#doc_ref.set({"Name": "Jesus", "Age": 38})
# %%
with open("strong_bios_v3.csv", "r") as file:
    csvreader = csv.reader(file)
    for i,row in enumerate(csvreader):
        if i < 50:
            print(row[0])
            res = ai.extract_topics(row[0])
            for n in res:
                doc_ref=db.collection(f"bios_{i}").document(n["topic"])
                doc_ref.set({"question": n["question"], "answer": n["answer"]})



# %%

ai.extract_topics("Hi, my name is Anna and I have worked and love to work with children! As a camp counselor leader I had to supervise children ranging from the ages of 6-12 years old during this summer camp program. Along with my team I made it my priority to lead group activities at times which included a variety of fun outdoor games. Besides having fun my priority was also to make sure the children were safe and out of harms way I had to make sure the group of kids were always around at all times. In Highschool I volunteered in a program which was a daycare for the children of some teachers. I had to plan activities for the children and curate lesson plans that would allow the children to learn and have fine. This includes motor activities depending on the age group which ranged from 2-5.  I have also taken care of multiple kids at a time and took charge of setting them to sleep. The most was 6 kids at a time from ages 6mo- 8 years old.  I'd describe my personality as loving, loyal, and responsible.")
# %%

## Dictionary with all data from firestore
#%%
bios_dict = {}
for i in range(50):
    doc_ref = db.collection(f"bios_{i}")
    for n in doc_ref.get():
        doc = doc_ref.document(n.id)
        bios_dict[n.id]=doc.get().to_dict()
# %%

## Get the most frequent questions:
#%%
freq_q = []
for i in range(50):
    doc_ref = db.collection(f"bios_{i}")
    for n in doc_ref.get():
        doc = doc_ref.document(n.id)
        freq_q.append(doc.get().to_dict()['question'])
# %%
fre_q_d=sorted(dict(Counter(freq_q)).items(), key=lambda x:x[1], reverse=True)
questions = dict(fre_q_d)
print(questions)


#%%
dict(itertools.islice(questions.items(), 5))

# %%
