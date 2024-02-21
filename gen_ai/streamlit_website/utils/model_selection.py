import streamlit as st

class ModelSelection:
    def __init__(self):
        pass
    
    def get_parameters_text(self):
        with st.sidebar:
            st.info("**Gemini or Bison ↓**", icon="✨")
            settings = ["gemini-pro", "text-bison@002", "text-bison-32k@002"]
            model = st.selectbox("Choose a text model",  settings, key="text_model_1")

            temperature = st.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="model_2", value=0.2) 
            if model == "gemini-pro":
                token_limit = st.select_slider("Token Limit", range(1,8193), key="text_token_1", value=1024)
            else:
                token_limit = st.select_slider("Token Limit", range(1, 1025), key="text_token_2", value=256)
            top_k = st.select_slider("Top-K", range(1, 41), key="text_top_k", value=40)
            top_p = st.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="text_top_p", value=0.8) 
            st.divider()
        
        parameters =  {
            "temperature": temperature,
            "max_output_tokens": token_limit,
            "top_p": top_p,
            "top_k": top_k
            }
        return model, parameters

    def get_parameters_chat(self):
        with st.sidebar:
            st.info("**Any Text Model here ↓**", icon="🤖")
            settings = ["chat-bison", "chat-bison-32k", "gemini-pro"]
            model = st.selectbox("Choose a text model",  settings, key="chat_model_1")

            temperature = st.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="chat_model_2", value=0.9) 
            if model == "gemini-pro" or model == "chat-bison-32k":
                token_limit = st.select_slider("Token Limit", range(1,8193), key="chat_token_1", value=1024)
            else:
                token_limit = st.select_slider("Token Limit", range(1, 2049), key="chat_token_2", value=1024)
            top_k = st.select_slider("Top-K", range(1, 41), key="chat_top_k", value=40)
            top_p = st.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="chat_top_p", value=0.8) 
            st.divider()
        
        parameters =  {
            "temperature": temperature,
            "max_output_tokens": token_limit,
            "top_p": top_p,
            "top_k": top_k
            }
        return model, parameters
        
    def get_parameters_all_models(self):
        with st.sidebar:
            st.info("**Any Text Model here ↓**", icon="🤖")
            settings = ["code-bison@002", "code-bison-32k@002", "text-bison@002", "text-bison-32k@002", "gemini-pro"]
            model = st.selectbox("Choose a model", settings, key="all_model")

            temperature = st.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="all_temperature", value=0.2) 
            if model == "code-bison@002" or model == "text-bison@002":
                    token_limit = st.select_slider("Token Limit", range(1, 2049), key="all_token1", value=1024)
            else: token_limit = st.select_slider("Token Limit", range(1,8193), key="all_token_1", value=2048)

            if "code" not in model:
                top_k = st.select_slider("Top-K", range(1, 41), key="all_topk", value=40)
                top_p = st.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="all_topp", value=0.8)
                parameters = {"temperature": temperature, "max_output_tokens": token_limit, "top_p": top_p, "top_k": top_k}

            else: parameters = {"temperature": temperature, "max_output_tokens": token_limit}    

        return model, parameters
    
    def get_parameters_32k_models(self):
        with st.sidebar:
            st.info("**Only 32k Models ↓**", icon="🤖")
            settings = ["gemini-pro", "text-bison-32k"]
            model = st.selectbox("Choose a model", settings, key="32k_model")
            temperature = st.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="all_temperature", value=0.2) 
            token_limit = st.select_slider("Token Limit", range(1,8193), key="all_token_1", value=5000)
            top_k = st.select_slider("Top-K", range(1, 41), key="all_topk", value=40)
            top_p = st.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="all_topp", value=0.8)
            
            parameters = {"temperature": temperature, "max_output_tokens": token_limit, "top_p": top_p, "top_k": top_k}

        return model, parameters
    
    
    def get_parameters_images(self):
        with st.sidebar:
            st.info("**Gemini MM & Vision ↓**", icon="🤖")
            settings = ["gemini-pro-vision", "imagetext"]
            model = st.selectbox("Choose a model", settings, key="32k_model")
            temperature = st.sidebar.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.2)     
            token_limit = st.sidebar.select_slider("Token Limit", range(1, 2049), value=2048)
            top_k = st.sidebar.select_slider("Top-K", range(1, 41), value=40)
            top_p = st.sidebar.select_slider("Top-P", range(1, 41), value=1)     
            
            parameters = {"temperature": temperature, "max_output_tokens": token_limit, "top_p": top_p, "top_k": top_k}    
        
        return model, parameters
    
    def get_parameters_for_tax(self):
        with st.sidebar:
            st.info("**LLM Orchestrator ↓**", icon="🤖")
            settings = ["gemini-pro", "gemini-ultra"]
            orch_model = st.selectbox("Choose a model", settings, key="tax_model_1")
            temperature = st.select_slider("Temperature", [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="tax_temperature_1", value=0.2) 
            token_limit = st.select_slider("Token Limit", range(1,8193), key="tax_token_1", value=5000)
            top_k = st.select_slider("Top-K", range(1, 41), key="tax_topk", value=40)
            top_p = st.select_slider("Top-P", [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="tax_top_p_1", value=0.8) 
            orch_params = {"temperature": temperature, "max_output_tokens": token_limit, "top_p": top_p, "tax_top_k_1": top_k}
            st.divider()
            
        with st.sidebar:
            st.info("**Complex Operations (Math Operations) ↓**", icon="✨")
            settings = ["text-unicorn@001", "gemini-pro"]
            comp_model = st.selectbox("Choose a text model",  settings, key="tax_model_2")

            temperature = st.select_slider("Temperature", [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="tax_temperature_2", value=0) 
            if comp_model == "gemini-pro":
                token_limit = st.select_slider("Token Limit", range(1,8193), key="tax_token_2", value=1024)
            else:
                token_limit = st.select_slider("Token Limit", range(1, 2049), key="tax_token_2", value=256)
            top_k = st.select_slider("Top-K", range(1, 41), key="tax_top_k_2", value=40)
            top_p = st.select_slider("Top-P", [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="tax_top_p_2", value=0.8)
            comp_params = {"temperature": temperature, "max_output_tokens": token_limit, "top_p": top_p, "tax_top_k_2": top_k}
            st.divider()

        with st.sidebar:
            st.info("**Other Operations (Agents) ↓**", icon="✨")
            settings = ["gemini-pro", "text-unicorn@001"]
            other_model = st.selectbox("Choose a text model",  settings, key="tax_model_3")

            temperature = st.select_slider("Temperature", [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="tax_temperature_3", value=0) 
            if other_model == "gemini-pro":
                token_limit = st.select_slider("Token Limit", range(1,8193), key="tax_token_3", value=8000)
            else:
                token_limit = st.select_slider("Token Limit", range(1, 2049), key="tax_token_3", value=2000)
            top_k = st.select_slider("Top-K", range(1, 41), key="text_top_k", value=40)
            top_p = st.select_slider("Top-P", [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="tax_top_p_3", value=0.8)
            other_params = {"temperature": temperature, "max_output_tokens": token_limit, "top_p": top_p, "tax_top_k_3": top_k}
            st.divider()
            
        
        return orch_model, comp_model, other_model, orch_params, comp_params, other_params