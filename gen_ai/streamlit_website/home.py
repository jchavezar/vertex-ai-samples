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
        st.markdown(""" + Document Q&A DIY [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/AvratanuBiswas/PubLit)""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + [Document Q&A]()  """)
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.text("")
        st.text("")
        st.text("")
        st.text("")

    with row_1_col2:
        st.markdown("""### News""")
        st.markdown(""" + [Multiturn News Feed]()  """)
        annotated_text(("multi-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + [Q&A (El Pais)]()  """)
        annotated_text(("single-turn", "", "#008744"), " ", ("spanish", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown(""" + [Multiturn El Pais](https://genai.sonrobots.net/News_RAG_[Vertex_Search])  """)
        annotated_text(("multi-turn", "", "#008744"), " ", ("spanish", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))

    row_2_col1, row_2_col2 = st.columns(2)

    with row_2_col1:
        st.markdown("""### Media & Ent""")
        st.markdown("""+ [Video Contextual Search](https://genai.sonrobots.net/Financial_RAG_[gecko-emb])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("multimodal", "", "#ffa700"))
        st.markdown("""+ [Movies Q&A](https://genai.sonrobots.net/Movies_QnA_[Vertex_Search])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "structured", "#ffa700"))

    with row_2_col2:
        st.markdown("""### Enterprise""")
        st.markdown("""+ [Analytics Using BiQuery Q&A](https://genai.sonrobots.net/Analytics_[BigQuery])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "structured", "#ffa700"))
        st.markdown("""+ [Generate your Caregiver Bio](https://genai.sonrobots.net/Caregiver_Bio_Gen[text-bison])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))

    row_3_col1, row_3_col2 = st.columns(2)

    with row_3_col1:
        st.markdown("""### Other""")
        st.markdown("""+ [Culture Reasoning and Action](https://genai.sonrobots.net/Culture_ReAct[vsearch_unicorn])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown("""+ [CrewAI Internet + Internal Q&A](https://genai.sonrobots.net/Any_Question_ReAct[vsearch_crewai])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("english", "", "#0057e7"), " ", ("OOB", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown("""+ [Reading 35 Pages Q&A](https://genai.sonrobots.net/BigFiles_[bison-32k])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown("""+ [Any Document Q&A](https://genai.sonrobots.net/Any_Doc_RAG[any-palm-model])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("text", "", "#ffa700"))
        st.markdown("""+ [Image Q&A](https://genai.sonrobots.net/Image_QnA_[vision]])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("image", "", "#ffa700"))
        st.markdown("""+ [Image Q&A](https://genai.sonrobots.net/Image_QnA_Gemini_MultiModal_[vision])""")
        annotated_text(("single-turn", "", "#008744"), " ", ("multi-language", "", "#0057e7"), " ", ("DIY", "", "#d62d20"), " ", ("multimodal", "", "#ffa700"))