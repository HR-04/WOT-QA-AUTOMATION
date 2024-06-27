import streamlit as st
import ollama
import json

st.title("Ollama Software Tester 🧑‍💻✨")

# Initial prompt for the assistant to act as a software tester
role_prompt = {
    "role": "system",
    "content": ("You are an expert software tester. When a user provides details of failed test case suites, "
                "analyze the failures, identify the root cause of the errors, and offer detailed suggestions to resolve them. "
                "Generate a Full solution code in TypeScript for the problem."
                "It's mandatory to provide full typescript code\n"
                "Provide clear, concise, and actionable insights in the following format:\n"
                "Root cause:\n"
                "explanation:\n"
                "suggestion:\n"
                "Full Code in Typescript with explanation")
}

if "messages" not in st.session_state:
    st.session_state["messages"] = [role_prompt, {"role": 'assistant', "content": "How can I assist you?"}]
    st.session_state["model"] = "llama3"  # Default model

# Sidebar for model selection using a dropdown
model_choice = st.sidebar.selectbox("Choose a model", ("llama3", "codellama"))

if model_choice and model_choice != st.session_state["model"]:
    st.session_state["model"] = model_choice
    st.success(f"Switched to {model_choice} model")

# Write Message History
for msg in st.session_state.messages:
    if msg['role'] != 'system':  # Skip displaying the role prompt
        if msg['role'] == 'user':
            st.chat_message(msg['role'], avatar="🧑‍💻").write(msg['content'])
        else:
            st.chat_message(msg['role'], avatar='🤖').write(msg['content'])

# Generator for streamlit token
def generate_response():
    response = ollama.chat(model=st.session_state["model"], stream=True, messages=st.session_state.messages)
    for partial_resp in response:
        token = partial_resp["message"]["content"]
        st.session_state["full_message"] += token
        yield token

if prompt := st.chat_input():
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    st.chat_message("user", avatar="🧑‍💻").write(prompt)
    st.session_state["full_message"] = ""
    st.chat_message('assistant', avatar="🤖").write_stream(generate_response)
    st.session_state.messages.append({'role': 'assistant', 'content': st.session_state["full_message"]})

# Clear chat history button
with st.sidebar:
    col1 , col2 = st.columns(2)
    
    with col1:
        submit1 = st.button("Clear Chat")



    # Save and load chat history
    with col2:
        submit2 = st.button("Save Chat")
    
if submit1:
    st.session_state.messages = [role_prompt, {"role": 'assistant', "content": "How can I assist you?"}]
    st.success("Chat history cleared")
    st.experimental_rerun()
    
if submit2:
    with open("chat_history.json", "w") as file:
        json.dump(st.session_state.messages, file)
    st.success("Chat history saved")

if st.sidebar.button("Load Chat"):
    with open("chat_history.json", "r") as file:
        st.session_state.messages = json.load(file)
    st.success("Chat history loaded")
    st.experimental_rerun()

# Generate plain text report for chat history
if st.sidebar.button("Generate Text Report"):
    report_lines = []
    for msg in st.session_state.messages:
        if msg['role'] != 'system':  # Skip the system role message
            report_lines.append(f"{msg['role'].capitalize()}:\n{msg['content']}\n")
    report_text = "\n".join(report_lines)

    st.download_button(
        label="Download Text Report",
        data=report_text,
        file_name="chat_history_report.txt",
        mime="text/plain"
    )


st.markdown(
    """
    <style>
    .stButton > button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)
