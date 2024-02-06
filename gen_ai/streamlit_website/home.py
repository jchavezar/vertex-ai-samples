import streamlit as st
from streamlit_extras.colored_header import colored_header
from annotated_text import annotated_text

def app():
    st.title('Content')
    
    #st.set_page_config(
    #    page_title="Generative AI",
    #    page_icon="👋",
    #)
#
    #colored_header(
    #    label=":blue[Google Cloud Generative AI] :sparkles: ",
    #    description="Google LLM Demos",
    #    color_name="red-80",
    #)

    st.sidebar.success("Select a demo above.")
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

    with st.expander("*Website Components and Architecture*"):
        st.image("images/genai_demos.png")

    with st.expander("*Wording*"):
        st.write(""":green[DIY]: Do it yourself, e.g. for RAG: **Using Document AI + gecko-embeddings + Vector Database**""")
        st.write(":green[OOB]: Out of the Box, e.g. for RAG: **Vertex Search**")

    row_1_col1, row_1_col2 = st.columns(2)
    sub_1, sub_2, sub_3, sub = st.columns(4)
    with row_1_col1:
        st.markdown("""### Financial""")
        st.markdown(""" + Document Q&A DIY $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/fin_rag_diy.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + Document Q&A OOB $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/fin_rag_oob.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.text("")
        st.text("")
        st.text("")
        st.text("")

    with row_1_col2:
        st.markdown("""### News""")
        st.markdown(""" + Multiturn News Feed $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/news_chatbot.py)""")
        annotated_text(("multi-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + Q&A (El Pais) $~~$  [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/news_elpais_qa.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("spanish", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + Multiturn (El Pais) $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/news_conv_elpais_qa.py)""")
        annotated_text(("multi-turn", "", "#008744"), " ", ("spanish", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))

    row_2_col1, row_2_col2 = st.columns(2)

    with row_2_col1:
        st.markdown("""### Media & Ent""")
        st.markdown(""" + Video Search $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/med_contex_search.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("multimodal", "", "#ffa700"))
        st.markdown(""" + Movies Q&A $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/movies_qa.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "structured", "#ffa700"))

    with row_2_col2:
        st.markdown("""### Enterprise""")
        st.markdown(""" + Analytics BQ Q&A $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/analytics_bq.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "structured", "#ffa700"))
        st.markdown(""" + Caregiver Bio Gen $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/ent_caregiver_bio.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))

    row_3_col1, row_3_col2 = st.columns(2)

    with row_3_col1:
        st.markdown("""### Other""")
        st.markdown(""" + LLM ReAct Q&A $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/culture_react.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + CrewAI Q&A $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/crewai_qa.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + Read 35 Pages Q&A $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/reading_35_pages.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + Ask your Document $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/ask_your_doc.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + Ask your Photo $~~$ [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/streamlit_website/ask_your_image.py)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("image", "", "#ffa700"))