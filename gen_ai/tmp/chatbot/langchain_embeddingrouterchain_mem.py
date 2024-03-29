#%%
#region Libraries
from vertexai.language_models import TextEmbeddingModel
import asyncio
import pandas as pd
import cloudsql_pgvector
import streamlit as st
import credentials, variables
from streamlit_chat import message
from typing import NamedTuple, List, Mapping, Optional
from langchain.chains.router.base import MultiRouteChain
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chains.router.embedding_router import EmbeddingRouterChain, RouterChain
from langchain.embeddings import VertexAIEmbeddings
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.llms import VertexAI
from langchain.chat_models import ChatVertexAI
from langchain.prompts import PromptTemplate
#endregion

#region Variables
var={
    "project_id":variables.PROJECT_ID,
    "region":variables.REGION,
    "database_name":variables.DATABASE_NAME,
    "instance_name":variables.INSTANCE_NAME,
    "database_user":variables.DATABASE_USER,
    "database_password":credentials.DATABASE_PASSWORD,
}

database=cloudsql_pgvector.Client(var)
emb_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
llm = VertexAI()
#endregion

#region Langchain Definition
class IntentModel(NamedTuple):
    """A model for an intent that a human may have."""

    intent: str
    description: str
    prompt: str
    default: bool = False  # is this the default or fallback intent?
    
class IntentRouterChain(MultiRouteChain):
    """Chain for routing inputs to different chains based on intent."""

    router_chain: RouterChain
    destination_chains: Mapping[str, LLMChain]
    default_chain: LLMChain

    @property
    def output_keys(self) -> List[str]:
        return ["text"]

    @classmethod
    def from_intent_models(
        cls,
        intent_models: List[IntentModel],
        llm: VertexAI,
        embedding_model: Optional[VertexAIEmbeddings],
        memory: Optional[ConversationBufferMemory] = None,
        verbose: bool = False,
    ) -> "IntentRouterChain":
        """Create a new IntentRouterChain from a list of intent models."""

        names_and_descriptions = [(i.intent, [i.description]) for i in intent_models]

        router_chain = EmbeddingRouterChain.from_names_and_descriptions(
            names_and_descriptions,
            DocArrayInMemorySearch,
            embedding_model,
            routing_keys=["input", "context"],
            verbose=verbose,
        )

        default_chain: Optional[LLMChain] = None
        destination_chains = {}
        for i in intent_models:
            destination_chains[i.intent] = LLMChain(
                llm=llm,
                prompt=PromptTemplate(
                    template=i.prompt, input_variables=["input", "chat_history", "context"]
                ),
                memory=memory,
            )
            if i.default:
                default_chain = destination_chains[i.intent]

        if not default_chain:
            raise ValueError("No default chain was specified.")

        return cls(
            router_chain=router_chain,
            destination_chains=destination_chains,
            default_chain=default_chain,
            verbose=verbose,
        )
        
#region templates
general_info = (
    "Here are the prior messages in this conversation:\n"
    "{chat_history}\n"
    "You are a a very funny and a joker and sometimes rude billing representative for a healthcare institution and your job is to assist humans with solving "
    "questions overall not related to any other topic.\n"
    "glue or match information from other intents and by using prior messages.\n"
    "disregard the following context : {context}"
    "\n"
    "Here is a question: {input}\n"
)

billing_template = (
    "You are a a very funny and a joker and sometimes rude billing representative for a healthcare institution and your job is to assist humans with solving "
    " questions about billing.\n"
    "These are some question examples: How to apply FA?, How to set up a payment plan?, etc..."
    "\n"
    "This is information about the following account 1985: payments: [100,200,300], owe: 400"
    "\n"
    "disregard the following context : {context}"
    "\n"
    "Here are the prior messages in this conversation:\n"
    "{chat_history}\n"
    "\n"
    "Here is a question: {input}\n"
)

get_support = (
    "You are a a very funny and a joker support agent for a insurance for a healthcare institution and your job is to assist humans with "
    "issues they may have related to insurance and memberships they have with us\n"
    "Here are some logs that will help you with your answer in the format of patient, provider/assistant: {context}"
    "\n"
    "Here are the prior messages in this conversation:\n"
    "{chat_history}\n"
    "\n"
    "Here is a question: {input}\n"
)

get_balance = (
    "Your job is to assist humans with"
    "getting information about their balance"
    "Here are some logs that will help you with your answer in the format of patient, provider/assistant: {context}"
    "\n"
    "Here are the prior messages in this conversation:\n"
    "{chat_history}\n"
    "\n"
    "Here is a question: {input}\n"
)


update_address = (
    "Your job is to assist humans with \n"
    "get the address \n"
    "update the address \n"
    "delete the address \n"
    f"These are your internal database registries: \n"
    " - Name: Jesus Chavez, Adress: 239 E 54 E New York New York. \n"
    " - Name: Jon Doe, Address: 100 W 14th New York New York. \n"
    "Do not fake data use only this data for addresses."
    "In your answer ask for your name and change the address by telling the old address in your response"
    "\n"
    "disregard the following context : {context}"
    "\n"
    "Here are the prior messages in this conversation:\n"
    "{chat_history}\n"
    "\n"
    "Here is a question: {input}\n"
)


#endregion

intent_models = [
    IntentModel(
        intent="General Info",
        description="the human has questions different from other intents",
        prompt=billing_template,
        default=True,
    ),
    IntentModel(
        intent="questions about billing account",
        description="the human has a question about billing, payments, etc...",
        prompt=billing_template,
    ),
    IntentModel(
        intent="needs support about insurance account",
        description="the human has a query about insurance",
        prompt=get_support,
    ),
    IntentModel(
        intent="questions about your balance",
        description="the human has a question about balance, financial breakdowns etc...",
        prompt=get_balance,
    ),
    IntentModel(
        intent="inquiries about address",
        description="the human has a query about profile",
        prompt=update_address,
    ),
]


# %%

#region context
def embeddings_search(prompt: str):
    ##### Query from Database Using LLM and Match with Embeddings
    qe = emb_model.get_embeddings([prompt])[0].values
    matches = asyncio.run(database.query(qe, table_name="hc_embeddings"))
    #Show the results for similar products that matched the user query.
    matches = pd.DataFrame(matches)
    return matches
#endregion

#region Streamlit
st.title("VertexAI-like Chatbot")

st.markdown("Welcome to **sockcop**, a bot capable of interact, route petitions and keep everything on memory.")
st.markdown("Here are some q examples:")
st.markdown("- What is the deductible for my insurance? - I have a question about my billing account.")
st.markdown("- I have a question about my billing account.")


if 'something' not in st.session_state:
    st.session_state.something = ''

def submit():
    st.session_state.something = st.session_state.input
    st.session_state.input = ''

query = st.text_input("Query:", key="input", on_change=submit)

st.write(f'Last submission: {st.session_state.something}')

if "responses" not in st.session_state:
    st.session_state["responses"] = []

if "requests" not in st.session_state:
    st.session_state["requests"] = []

if "buffer_memory" not in st.session_state:
    st.session_state.buffer_memory = ConversationBufferMemory(
        memory_key="chat_history", 
        input_key="input",
        return_messages=True
    )

chain = IntentRouterChain.from_intent_models(
    intent_models=intent_models,
    llm=llm,
    embedding_model=VertexAIEmbeddings(),
    memory=st.session_state.buffer_memory,
    verbose=True,
)

if st.session_state.something:
    response = chain.run(input =  st.session_state.something, context = "text")
    st.session_state.requests.append( st.session_state.something)
    st.session_state.responses.append(response)

if st.session_state["responses"]:

    for i in range(len(st.session_state["responses"])-1, -1, -1):
        message(st.session_state["requests"][i], is_user=True, key=str(i) + "_user")
        message(st.session_state["responses"][i], key=str(i))
#endregion