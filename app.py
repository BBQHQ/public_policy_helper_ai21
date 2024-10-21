import streamlit as st
import pandas as pd
import json
import requests

def call_ai21_api(prompt):
    if 'AI21_API_KEY' not in st.secrets:
        st.error("AI21 API key not found in Streamlit secrets.")
        return None

    api_key = st.secrets['AI21_API_KEY']
    url = 'https://api.ai21.com/studio/v1/chat/completions'
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        "model": "jamba-1.5-large",
        "messages": [{"role": "user", "content": prompt}],
        "documents": [],
        "tools": [],
        "n": 1,
        "max_tokens": 2048,
        "temperature": 0.4,
        "top_p": 1,
        "stop": [],
        "response_format": {"type": "text"},
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['outputs'][0]['text']
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling AI21 API: {e}")
        return None

def main():
    st.title("Streamlit App with AI21 Integration")
    
    st.write("This app demonstrates pandas, json, and direct AI21 API integration.")
    
    # Example using pandas
    df = pd.DataFrame({
        'Column 1': [1, 2, 3, 4],
        'Column 2': ['A', 'B', 'C', 'D']
    })
    st.write("Sample DataFrame:")
    st.dataframe(df)
    
    # Example using json
    sample_json = {
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    }
    st.write("Sample JSON:")
    st.json(sample_json)
    
    # AI21 Integration
    st.write("AI21 Integration:")
    user_prompt = st.text_input("Enter a prompt for AI21:", "Tell me a short joke.")
    if st.button("Generate Text with AI21"):
        with st.spinner("Generating response..."):
            response = call_ai21_api(user_prompt)
            if response:
                st.write("AI21 Response:")
                st.write(response)

if __name__ == "__main__":
    main()