import openai
import json
import os
from function_call import *

TICKERS = {"GM": "General Motors"}


with open("credentials.json") as f:
    creds = json.load(f)
    openai.organization = creds["org_id"]
    openai.api_key = creds["openai_api"]
    os.environ["OPENAI_API_KEY"] = creds["openai_api"]

def initialize_state(st):
    # Initialise session state variables
    if 'tickers' not in st.session_state:
        st.session_state['tickers'] = []
    
    if 'current_ticker' not in st.session_state:
        st.session_state['current_ticker'] = ''
    
    if 'ticker_states' not in st.session_state:
        st.session_state['ticker_states'] = {}
    

def initialize_ticker(st, ticker):

    if ticker not in st.session_state['ticker_states']:
        st.session_state['ticker_states'][ticker] = {}
    if 'generated' not in st.session_state['ticker_states'][ticker]:
        st.session_state['ticker_states'][ticker]['generated'] = []
    if 'past' not in st.session_state['ticker_states'][ticker]:
        st.session_state['ticker_states'][ticker]['past'] = []
    if 'messages' not in st.session_state['ticker_states'][ticker]:
        st.session_state['ticker_states'][ticker]['messages'] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
 
def reset_state(st, ticker):
    del st.session_state['ticker_states'][ticker]
    all_tickers  = st.session_state['tickers']
    del st.session_state['tickers'][all_tickers.index(ticker)]
    st.session_state['current_ticker'] = ''

def generate_response(prompt, ticker, st):   
    # Step 1: send the conversation and available functions to GPT
    st.session_state['ticker_states'][ticker]['messages'].append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        functions=FUNCTIONS,
        function_call="auto",
        messages=st.session_state['ticker_states'][ticker]['messages']
    )

    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "create_price_volume_chart": create_price_volume_chart,
            "create_price_chart": create_price_chart,
            "create_volume_chart": create_volume_chart,
            "context_fetcher": context_fetcher,
            "financial_reports_answerer": financial_reports_answerer,
            "create_revenue_comparator": create_revenue_comparator,
            "create_growthchart": create_growthchart,
            "universe_correlator":universe_correlator,
        }
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        if function_name in ("create_price_volume_chart", "create_price_chart", 
                             "create_volume_chart", 
                             "create_growthchart"):
            function_response, fig = function_to_call(
                ticker=function_args.get("ticker"),
                name=function_args.get("name"),
            )
            
        elif function_name in ("context_fetcher"):
            function_response = function_to_call(
                ticker=function_args.get("ticker")
            )
        
        elif function_name in ("financial_reports_answerer"):
            output, function_response = function_to_call(
                ticker=function_args.get("ticker"),
                prompt=function_args.get("prompt")
            )

        elif function_name in ("create_revenue_comparator"):
            function_response, fig = function_to_call(
                ticker1=function_args.get("ticker1"),
                ticker2=function_args.get("ticker2"),
            )
        
        elif function_name in ("universe_correlator"):
            #print(function_args) #for debugging
            function_response, fig = function_to_call(
                    tickers=json.loads(function_args.get("tickers")),
                    sector=function_args.get("sector"),
                    hierarchical=function_args.get("hierarchical")                
                )

        # Step 4: send the info on the function call and function response to GPT
        st.session_state['ticker_states'][ticker]['messages'].append(response_message)
        st.session_state['ticker_states'][ticker]['messages'].append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response

        response_message2 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=st.session_state['ticker_states'][ticker]['messages'],
        )["choices"][0]["message"]  # get a new response from GPT where it can see the function response


        if function_name in ("context_fetcher"):
            st.session_state['ticker_states'][ticker]['messages'].append({"role": "assistant", "content": response_message2.content})
            return response_message2.content
        elif function_name in ("financial_reports_answerer"):
            # Do not feed this answer back into the msg history because AI can hallucinate on this. 
            ### st.session_state['ticker_states'][ticker]['messages'].append({"role": "assistant", "content": response_message2.content})
            return output
        else:
            return [fig]

    st.session_state['ticker_states'][ticker]['messages'].append({"role": "assistant", "content": response_message.content})
    return response_message.content

    # response = completion.choices[0].message.content
    # st.session_state['ticker_states'][ticker]['messages'].append({"role": "assistant", "content": response})
    # return response
