import streamlit as st
import os
from langchain_community.llms import Ollama

# Initialize the model
model = Ollama(model="codellama")

# Function to convert roles to Streamlit-compatible roles
def role_to_streamlit(role):
    if role == "model":
        return "assistant"
    else:
        return role

# Initialize chat history in session state if not already done
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Title of the Streamlit app
st.title("WOT_QA_AUTOMATION✨")

# Instruction to the model (acting as a chat template)
template_instruction = (
    "You are an expert software tester. When a user provides details of failed test case suites, "
    "analyze the failures, identify the root cause of the errors, and offer detailed suggestions to resolve them. "
    "Provide clear, concise, and actionable insights."
)

# Add instruction to the chat history if it's the first message
if not st.session_state.chat_history:
    st.session_state.chat_history.append({
        "role": "system",
        "content": template_instruction
    })

# Display the chat history
for message in st.session_state.chat_history:
    with st.chat_message(role_to_streamlit(message["role"])):
        st.markdown(message["content"])

# Input for user message
if prompt := st.chat_input("Message QueryCrafter..."):
    st.chat_message("user").markdown(prompt)
    
    # Send the prompt to the model
    response = model.chat(prompt, history=st.session_state.chat_history)
    
    # Append the user prompt and assistant response to the chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt
    })
    st.session_state.chat_history.append({
        "role": "model",
        "content": response["text"]
    })
    
    # Display the assistant's response
    with st.chat_message("assistant"):
        st.markdown(response["text"])

# Sidebar with a button to clear chat history
with st.sidebar:
    if st.button("Clear History"):
        st.session_state.chat_history.clear()
        # Re-add the instruction after clearing history
        st.session_state.chat_history.append({
            "role": "system",
            "content": template_instruction
        })
