import streamlit as st
from util import *

# Setting page title and header
st.set_page_config(page_title="Stockly")
st.markdown("<h1 style='text-align: center;'> Start your investment research right now! </h1>", unsafe_allow_html=True)

initialize_state(st)

user_input = st.text_area("Enter Ticker:", key='input').strip()

if user_input:
    st.session_state['tickers'].append(user_input)

st.write(st.session_state['tickers'])
st.session_state['current_ticker'] = user_input

## Todo: Redirect to the stocks page if the user actually entered a ticker