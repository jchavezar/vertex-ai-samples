#%%
import vertexai
import streamlit as st
from vertexai.preview.generative_models import GenerativeModel, Part

col1, col2 = st.columns([10,4])

#region Gemini Pro
def generate(prompt):
  model = GenerativeModel("gemini-pro")
  response = model.generate_content(
    f"""you are a journalist. you write articles about any topic on online portals. you write your articles based on {prompt} only. You donot add additional information or clarification. Donot generate any links to webpages. Donot generate hyperlinks. your articles are positive in tone and highlight positive aspects about the topic. You never criticise the topic or take negative aspects about topic. Your articles comprise of three paragraphs.
Write an article in spanish
input_text :""",
    generation_config={
        "max_output_tokens": 2048,
        "temperature": 0.9,
        "top_p": 1
    },
  )
  
  return response.text
#end_region


def image_gen_model(prompt, sampleImageSize, sampleCount, endpointType='Prod', seed=None):
  response=""
  headers = {
      'Authorization': f'Bearer {ACCESS_TOKEN}',
      'Content-Type': 'application/json; charset=UTF-8'
  }
  # Advanced option, try different the seed numbers
  # any random integer number range: (0, 2147483647)
  if seed==None:
    data = {"instances": [{"prompt": prompt}],"parameters": {"sampleImageSize": sampleImageSize,"sampleCount": sampleCount}}
  else:
    # Use & provide a seed, if possible, so that we can reproduce the results when needed.
    data = {"instances": [{"prompt": prompt}],"parameters": {"sampleImageSize": sampleImageSize,"sampleCount": sampleCount, "seed": seed}}

  print(data)
  if endpointType=='Prod':
    # Prod usage
    response = requests.post(ENDPOINT_URL, data=json.dumps(data), headers=headers)
  return response


with st.container():
    prompt = st.text_input(label = "Tema para las Noticias")
    res = generate(prompt)
    # %%

with st.container():
    panel1 = col1.empty()
    panel2 = col2.empty()
    
    with panel1.container():
        st.write(res)
    with panel2.container():
        st.write("text")