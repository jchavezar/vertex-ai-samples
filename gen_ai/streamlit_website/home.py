import os
import streamlit as st
from utils.links_references import *
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
        st.markdown(f""" + Document Q&A DIY $~~$ [![Repo]({github_icon})]({fin_rag_diy})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(f""" + Document Q&A OOB $~~$ [![Repo]({github_icon})]({fin_rag_oob})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.text("")
        st.text("")
        st.text("")
        st.text("")

    with row_1_col2:
        st.markdown("""### News""")
        st.markdown(f""" + Multiturn News Feed $~~$ [![Repo]({github_icon})]({news_chatbot})""")
        annotated_text(("multi-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(f""" + Q&A (El Pais) $~~$  [![Repo]({github_icon})]({news_elpais_qa})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("spanish", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(f""" + Multiturn (El Pais) $~~$ [![Repo]({github_icon})]({news_conv_elpais_qa})""")
        annotated_text(("multi-turn", "", "#008744"), " ", ("spanish", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))

    row_2_col1, row_2_col2 = st.columns(2)

    with row_2_col1:
        st.markdown("""### Media & Ent""")
        st.markdown(f""" + Video Search $~~$ [![Repo]({github_icon})]({med_contex_search})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("multimodal", "", "#ffa700"))
        st.markdown(f""" + Movies Q&A $~~$ [![Repo]({github_icon})]({movies_qa})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "structured", "#ffa700"))

    with row_2_col2:
        st.markdown("""### Enterprise""")
        st.markdown(f""" + Analytics BQ Q&A $~~$ [![Repo]({github_icon})]({analytics_bq})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "structured", "#ffa700"))
        st.markdown(f""" + Caregiver Bio Gen $~~$ [![Repo]({github_icon})]({ent_caregiver_bio})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))

    row_3_col1, row_3_col2 = st.columns(2)

    with row_3_col1:
        st.markdown("""### Other""")
        st.markdown(f""" + LLM ReAct Q&A $~~$ [![Repo]({github_icon})]({culture_react})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(f""" + CrewAI Q&A $~~$ [![Repo]({github_icon})]({crewai_qa})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(f""" + Read 35 Pages Q&A $~~$ [![Repo]({github_icon})]({reading_35_pages})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(f""" + Ask your Document $~~$ [![Repo]({github_icon})]({ask_your_doc})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(f""" + Ask your Photo $~~$ [![Repo]({github_icon})]({ask_your_image})""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("image", "", "#ffa700"))