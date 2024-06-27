import streamlit as st
import ollama
import json
import pandas as pd

st.title("Ollama Software Tester 🧑‍💻✨")

# Initial prompt for the assistant to act as a software tester
role_prompt = {
    "role": "system",
    "content": ("You are an expert software tester. When a user provides details of failed test case suites, "
                "analyze the failures, identify the root cause of the errors, and offer detailed suggestions to resolve them. "
                "Provide clear, concise, and actionable insights in the following format:\n"
                "Root cause:\n"
                "explanation:\n"
                "suggestion:")
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


with st.sidebar:

    col1,col2 = st.columns(2)

    # Clear chat history button
    with col1:
        submit1 = st.button("Clear Chat History")

    # Save and load chat history
    with col2:
        submit2 = st.button("Save Chat History")
        
    

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

if st.sidebar.button("Load Chat History"):
    with open("chat_history.json", "r") as file:
        st.session_state.messages = json.load(file)
    st.success("Chat history loaded")
    st.rerun()


if submit1:
    st.session_state.messages = [role_prompt, {"role": 'assistant', "content": "How can I assist you?"}]
    st.success("Chat history cleared")
    st.rerun()
    
if submit2:
    with open("chat_history.json", "w") as file:
        json.dump(st.session_state.messages, file)
    st.success("Chat history saved")

# Upload test case suite
uploaded_file = st.sidebar.file_uploader("Upload Test Case Suite", type=["json", "csv"])

if uploaded_file:
    if uploaded_file.type == "application/json":
        test_cases = json.load(uploaded_file)
    elif uploaded_file.type == "text/csv":
        test_cases = pd.read_csv(uploaded_file).to_dict(orient="records")

    st.write("Uploaded Test Case Suite:")
    st.json(test_cases)

    # Analyze test cases
    st.session_state.messages.append({'role': 'user', 'content': f"Analyze the following test cases:\n{test_cases}"})
    st.session_state["full_message"] = ""
    st.chat_message('assistant', avatar="🤖").write_stream(generate_response)
    st.session_state.messages.append({'role': 'assistant', 'content': st.session_state["full_message"]})

# Generate TypeScript solution code and explanation
if st.sidebar.button("Generate Code"):
    with st.spinner("Generating code..."):
        st.session_state.messages.append({'role': 'user', 'content': 'Generate a solution code in TypeScript for the problem.'})
        st.session_state["full_message"] = ""
        st.chat_message('assistant', avatar="🤖").write_stream(generate_response)
        st.session_state.messages.append({'role': 'assistant', 'content': st.session_state["full_message"]})
        generated_code = st.session_state["full_message"]

    st.code(generated_code, language='typescript')

    # Allow user to create a downloadable solution text file
    if st.button("Create Solution Text File"):
        st.download_button(
            label="Download Solution Code",
            data=generated_code,
            file_name="solution_code.txt",
            mime="text/plain"
        )
