import streamlit as st
from sem2 import router
from faq import ingest_faq_data,faq_chain
from sql import sql_chain

ingest_faq_data('/Users/rohandesu/ecom/app/resources/faq_data.csv')
def ask(query):
    route=router(query).name
    if route=='faq':
        return faq_chain(query)
    else:
        return sql_chain(query)


st.title('E commerce chat bot')

query=st.chat_input("write your query")

if "messages" not in st.session_state:
    st.session_state["messages"]=[]
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
if query:
    with st.chat_message("user"):
        st.markdown(query)
        st.session_state['messages'].append({'role':'user','content':query})

    response=ask(query)
    with st.chat_message("assistant"):
        st.markdown(response)
        st.session_state['messages'].append({'role':'assistant','content':response})
