import streamlit as st
import requests
import os
import re
import json

# Access the API key from Streamlit secrets
API_KEY = st.secrets["AI21_API_KEY"]

def call_ai21_api(prompt):
    url = 'https://api.ai21.com/studio/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "jamba-1.5-large",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 5000,
        "temperature": 0.3,
        "top_p": 1
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling AI21 API: {e}")
        return None

def clean_text(text):
    text = re.sub(r'[®©™]', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return clean_text(content)

def generate_prompt_template(selected_files, question):
    prompt_template = "#################################\n"
    for i, file in enumerate(selected_files, 1):
        file_path = os.path.join('./data', file)
        file_content = read_file(file_path)
        plan_name = os.path.splitext(file)[0]
        
        prompt_template += f"PLAN: {plan_name}\n"
        prompt_template += f"PLANDETAILS: {file_content}\n"
        prompt_template += "#################################\n\n"
    
    if question:
        prompt_template += "#################################\nCOMPARE THE ABOVE HEALTHCARE PLANS AND ANSWER THIS QUESTION:\n"
        prompt_template += clean_text(question)
    
    return prompt_template

def escape_markdown(text):
    chars_to_escape = ['$', '*', '_', '[', ']', '(', ')', '#', '+', '-', '.', '!']
    for char in chars_to_escape:
        text = text.replace(char, '\\' + char)
    return text

def main():
    st.title("Integrated AI21 API and Prompt Template Generator")

    # Prompt Template Generator Section
    st.header("Prompt Template Generator")
    
    data_folder = './data'
    txt_files = [f for f in os.listdir(data_folder) if f.endswith('.txt')]
    
    selected_files = st.multiselect("Select up to 2 files", txt_files, max_selections=2)
    question = st.text_area("Enter your question for plan comparison")
    
    if selected_files:
        prompt_template = generate_prompt_template(selected_files, question)
        st.text_area("Generated Prompt Template", prompt_template, height=200)
        st.session_state.generated_prompt = prompt_template

    # AI21 API Section
    st.header("AI21 API Response")
    
    use_generated_prompt = st.checkbox("Use generated prompt", value=bool(st.session_state.get('generated_prompt', '')))
    
    if use_generated_prompt and 'generated_prompt' in st.session_state:
        user_prompt = st.session_state.generated_prompt
        st.text_area("Prompt to be sent", user_prompt, height=100)
    else:
        user_prompt = st.text_area("Enter your prompt:", height=100)

    if st.button("Get AI Response"):
        if not user_prompt:
            st.warning("Please enter a prompt or generate one using the Prompt Template Generator.")
        else:
            with st.spinner("Generating response..."):
                response = call_ai21_api(user_prompt)
                
                if response:
                    try:
                        if 'choices' in response and len(response['choices']) > 0:
                            choice = response['choices'][0]
                            if 'message' in choice:
                                message = choice['message']['content']
                            elif 'messages' in choice:
                                message = choice['messages']
                            elif 'mesages' in choice:  # Handle potential typo in key name
                                message = choice['mesages']
                            else:
                                message = str(choice)  # Fallback: convert the entire choice to string
                        else:
                            message = str(response)  # Fallback: convert the entire response to string
                        
                        st.subheader("AI Response:")
                        escaped_message = escape_markdown(message)
                        st.write(escaped_message)
                        
                        # Option to view full API response
                        with st.expander("View Full Response"):
                            st.json(response)
                    except KeyError as e:
                        st.error(f"Failed to parse response: {e}")
                        st.json(response)

if __name__ == "__main__":
    if 'generated_prompt' not in st.session_state:
        st.session_state.generated_prompt = ""
    
    main()