
import base64
import streamlit as st
from google.cloud import aiplatform

prompt=st.text_input("Your prompt", key="name")
instances={"instances": [prompt]}
endpoint=aiplatform.Endpoint("projects/254356041555/locations/us-central1/endpoints/2543445272952832000")

if st.button(r'Generate'):
    images=endpoint.predict(instances)
    with open("hamburguer-2.jpeg", "wb") as f:
        f.write(base64.b64decode(images.predictions[0]))
    st.image("hamburguer-2.jpeg")