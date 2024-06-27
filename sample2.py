import streamlit as st
import ollama
import json
from fpdf import FPDF

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

# Clear chat history button
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = [role_prompt, {"role": 'assistant', "content": "How can I assist you?"}]
    st.success("Chat history cleared")
    st.experimental_rerun()

# Save and load chat history
if st.sidebar.button("Save Chat History"):
    with open("chat_history.json", "w") as file:
        json.dump(st.session_state.messages, file)
    st.success("Chat history saved")

if st.sidebar.button("Load Chat History"):
    with open("chat_history.json", "r") as file:
        st.session_state.messages = json.load(file)
    st.success("Chat history loaded")
    st.experimental_rerun()

# Generate PDF report for chat history
class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, "Chat History Report", 0, 1, "C")

    def chapter_title(self, title):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(10)

    def chapter_body(self, body):
        self.set_font("DejaVu", "", 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_message(self, role, content):
        self.add_page()
        self.chapter_title(f"{role.capitalize()} says:")
        self.chapter_body(content)

if st.sidebar.button("Generate PDF Report"):
    pdf = PDF()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    for msg in st.session_state.messages:
        if msg['role'] != 'system':  # Skip the system role message
            pdf.add_message(msg['role'], msg['content'])

    pdf_output = pdf.output(dest='S').encode('utf-8')
    st.download_button(
        label="Download PDF Report",
        data=pdf_output,
        file_name="chat_history_report.pdf",
        mime="application/pdf"
    )

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
