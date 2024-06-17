import streamlit as st
from typing import Generator
from groq import Groq
import json

client = Groq(
    api_key='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',
)

with open('insurance_db.json', 'r') as file:
    data = json.load(file)
data = json.dumps(data)

st.set_page_config(page_icon="🚑", layout="wide",
                   page_title="Insurance AI Agent")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

icon(":male-doctor:")

st.header("Vishwas - Your Personal Insurance AI Agent", divider="rainbow", anchor=False)

st.subheader("Vishwas is a smart Insurance Agent that you can use to answer your queries about any of our insurance products, general information and even purchase an insurance policy! Feel free to interact with Vishwas and ask for anything you want!",
             anchor=False
             )
# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []
msg_counter = 0 


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Display chat messages from history on app rerun
for message in st.session_state.messages[1::]:
    avatar = '🤖' if message["role"] == "assistant" else '⚕️'
    with st.chat_message(message["role"], avatar=avatar):
        if msg_counter>0:
            msg_counter+=1
            st.markdown(message["content"])
        elif msg_counter == 0 :
            st.markdown(st.session_state.messages[1]['content'])
        #if 'whoami' not in message['content'][:10:] : 
            msg_counter+=1
            
            
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": data})
    try:
        # Fetch response from Groq API
        res = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            max_tokens=8192,
            stream=True
        )
        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(res)
            full_response = st.write_stream(chat_responses_generator)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(e, icon="🚨")
            

if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="⚕️"):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model='llama3-70b-8192',
            messages= [
                {
                    "role": m["role"],
                    "content": m["content"]
                } 
                for m in st.session_state.messages
            ],
            max_tokens=8192,
            stream=True
        )
        # for m in st.session_state.messages[-1]:
        #     print('\n\n\n\n\n\n\n\n\n', m['content'])
        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(e, icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})
