import streamlit as st

text = st.empty()
value = "Get internal information about building policies like trash collection, packages pickup, ammenities use and dogs animal polices"
if st.button('reset', type="primary"):
    value = "Get internal information about building policies like trash collection, packages pickup, ammenities use and dogs animal polices"

text.text_area("Write your info here:", value)


button = st.button("test")

import streamlit as st
# ...code...
if 'area_key' not in st.session_state:
    st.session_state.area_key = 1

prompt_text_placeholder = st.empty()
with prompt_text_placeholder.container():
    prompt_text = st.text_area(label="User",
                     height=100,
                     value="Get internal information about building policies like trash collection, packages pickup, ammenities use and dogs animal polices", key=st.session_state.area_key)

# your chat code
if button:
    # when chat complete
    st.session_state.area_key += 1
    prompt_text_placeholder.empty()
    with prompt_text_placeholder.container():
        prompt_text = st.text_area(label="User",
                        height=100,
                        value="Get internal information about building policies like trash collection, packages pickup, ammenities use and dogs animal polices",
                        key=st.session_state.area_key)