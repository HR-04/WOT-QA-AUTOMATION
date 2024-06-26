import streamlit as st
import ollama
import os

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

# Sidebar button to generate TypeScript solution code and explanation
if st.sidebar.button("Generate Code"):
    with st.spinner("Generating code..."):
        st.session_state.messages.append({'role': 'user', 'content': 'Generate a solution code in TypeScript for the problem.'})
        st.session_state["full_message"] = ""
        st.chat_message('assistant', avatar="🤖").write_stream(generate_response)
        st.session_state.messages.append({'role': 'assistant', 'content': st.session_state["full_message"]})
        generated_code = st.session_state["full_message"]

    st.code(generated_code, language='typescript')

    # Allow user to create a solution text file
    if st.button("Create Solution Text File"):
        # Example content for root cause, explanation, suggestion, and code explanation
        root_cause = "Example root cause explanation"
        explanation = "Example detailed explanation"
        suggestion = "Example suggestions to resolve the issue"
        code_explanation = "Example explanation of the generated solution code"

        solution_text = (
            f"Root cause:\n{root_cause}\n\n"
            f"Explanation:\n{explanation}\n\n"
            f"Suggestion:\n{suggestion}\n\n"
            f"Solution code:\n{generated_code}\n\n"
            f"Code explanation:\n{code_explanation}"
        )

        # Specify the path to save the file
        directory_path = "F:\\Qsek_Intern\\WOT-QA-AUTOMATION\\sample_response"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        
        file_path = os.path.join(directory_path, "solution.txt")
        with open(file_path, 'w') as file:
            file.write(solution_text)

        st.success(f"Solution text file created at {file_path}")
        st.text(solution_text)
