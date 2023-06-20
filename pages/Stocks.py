import streamlit as st
from streamlit_chat import message
from util import *

# Setting page title and header
st.set_page_config(page_title="Stockly")
initialize_state(st)

import random



SAMPLE_PROMPTS = ["Can you show me the price and volume of GM over time?", 
                  "Can you show me the volume of GM over the last 6 months?", 
                  "What is the recent news sentiment on GM?", 
                  "Tell me about the biggest risks for GM's profitability.", 
                  "Plot the growth in net income of GM",
                  "Who is the CEO of GM?", 
                  "Which risks are mentioned in the latest annual report of GM", 
                  "Compare revenue of GM to APPLE",
                #   "Can you name 10 companies similar to GM in europe?",
                  "How do automotive companies compare? Please check correlations",
                  "Can you please analyze aerospace companies and their hierarchy for me?",
                  ]

RAND_PRO = random.sample(SAMPLE_PROMPTS, 3)

my_ticker = st.session_state['current_ticker']
all_tickers  = st.session_state['tickers']

# If my_ticker is empty, just pick the first one
if my_ticker == '' and len(all_tickers) > 0:
    my_ticker = all_tickers[0]

st.sidebar.title("Your Research")
if my_ticker != '':
    input_ticker = st.sidebar.radio('Open Tickers:', all_tickers, index = all_tickers.index(my_ticker))

    if input_ticker != my_ticker:
        st.session_state['current_ticker'] = input_ticker
        st.experimental_rerun()

    # Check if user wants to delete this ticker tab
    clear_button = st.sidebar.button("Close Research", key="clear")
    if clear_button:
        reset_state(st, my_ticker)
        st.experimental_rerun()

# If my_ticker is empty, just pick the first one
if my_ticker == '' and len(all_tickers) > 0:
    my_ticker = all_tickers[0]

st.session_state['current_ticker'] = my_ticker

if my_ticker == '':
    st.markdown(f"<h1 style='text-align: center;'> Go to Home and start a new research right now! </h1>", unsafe_allow_html=True)

else:
    st.markdown(f"<h1 style='text-align: center;'> {my_ticker} </h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: left;'> Suggestions: </h4>", unsafe_allow_html=True)
    butt_user_input = ''

    if 'ps' in st.session_state:
        rand_ps = st.session_state['ps']
    else:
        rand_ps = RAND_PRO
        st.session_state['ps'] = rand_ps

    if st.button(f"{rand_ps[0]}"):
        butt_user_input = rand_ps[0]
        del st.session_state['ps']

    if st.button(f"{rand_ps[1]}"):
        butt_user_input = rand_ps[1]
        del st.session_state['ps']

    if st.button(f"{rand_ps[2]}"):
        butt_user_input = rand_ps[2]
        del st.session_state['ps']

    print(butt_user_input)
    initialize_ticker(st, my_ticker)

    # container for chat history
    response_container = st.container()
    # container for text box
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_area("You:", key='input', height=100)
            submit_button = st.form_submit_button(label='Send')

        if (submit_button and user_input) or butt_user_input != '':
            user_input = user_input if user_input else butt_user_input
            output = generate_response(user_input, my_ticker, st)
            st.session_state['ticker_states'][my_ticker]['past'].append(user_input)
            if type(output) is str:
                st.session_state['ticker_states'][my_ticker]['generated'].append(output)
            else:
                st.session_state['ticker_states'][my_ticker]['generated'].extend(output)
            
            st.experimental_rerun()

        if st.session_state['ticker_states'][my_ticker]['generated']:
            with response_container:
                for i in range(len(st.session_state['ticker_states'][my_ticker]['generated'])):
                    p = st.session_state['ticker_states'][my_ticker]['past'][i]
                    g = st.session_state['ticker_states'][my_ticker]['generated'][i]
                    if type(p) is not str:
                        st.write(p)
                    else:
                        message(p, is_user=True, key=str(i) + '_user')

                    if type(g) is not str:
                        st.write(g)
                    else:
                        message(g, key=str(i))

    st.write(st.session_state['ticker_states'][my_ticker]['messages'])