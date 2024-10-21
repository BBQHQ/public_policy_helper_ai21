import streamlit as st
import pandas as pd
import json
import requests
import os

# Function to read insurance plans from local files
def get_insurance_plans():
    plans = []
    data_folder = 'data'  # Assuming your data is in a 'data' folder
    for filename in os.listdir(data_folder):
        if filename.endswith('.txt'):
            plans.append(filename[:-4])  # Remove '.txt' extension
    return sorted(plans)

# Function to read plan details from file using UTF-8 encoding
def read_plan_details(plan_name):
    file_path = os.path.join('data', f"{plan_name}.txt")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # If UTF-8 decoding fails, use error handler to replace problematic characters
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            return file.read()

# Function to call AI21 API (Jamba)
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
        "max_tokens": 5000,
        "temperature": 0.3,
        "top_p": 1,
        "stop": [],
        "response_format": {"type": "text"},
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling AI21 API: {e}")
        return None

# Main app
def main():
    st.title("Insurance Plan Comparison with Jamba-1.5-Large")

    st.write("""
    Welcome to the Insurance Plan Comparison App! This tool empowers you to compare various healthcare plans using detailed plan information loaded from local files. With the help of the Jamba-1.5-Large model, you can pose specific questions to guide your decision-making process. Whether your focus is on out-of-pocket costs, prescription coverage, or options for families, this app facilitates the comparison of up to two plans simultaneously!

    For more information about specific plans, you can access the [coverage policy documents here](https://www.bluecrossma.org/myblue/learn-and-save/plans-and-benefits/coverage-policy-documents).
    """)

    # Get all available plans
    all_plans = get_insurance_plans()

    # Allow user to select up to 2 plans
    selected_plans = st.multiselect("Select up to 2 plans to compare:", all_plans, max_selections=2)

    st.write("""
    Below, you can select one of the pre-canned questions or enter your own custom question. 
    The app uses this question to analyze the selected plans and provide a tailored response.
    """)

    # Pre-canned questions
    pre_canned_questions = [
        "I need an in-patient procedure, help me choose which plan is best for me?",
        "Which healthcare plan should I choose between these 2?",
        "How much would I pay out of pocket to see my PCP every year?",
        "I have a large family with 4 dependents. Which plan is right for me?",
        "How much prescription coverage is paid for by each of these plans?",
        "I am over 18 years old and the only person who would be covered by my insurance. Is vision covered by these insurance plans?",
        "Custom question"
    ]

    # Dropdown for pre-canned questions
    selected_question = st.selectbox("Select a pre-canned question or choose 'Custom question':", pre_canned_questions)

    st.markdown("---")
    st.header("HC Plan Comparison Question")

    # Text input for user's question
    if selected_question == "Custom question":
        question = st.text_input("Enter your custom question about the selected plans:")
    else:
        question = st.text_input("Question about the selected plans:", value=selected_question)

    st.write("""
    The model response will appear below, offering detailed comparisons based on your selected question and plans. 
    You can expand the 'View Full Response' section to see the complete model output in JSON format.
    """)

    # Button to run the comparison
    if st.button('Compare Plans') and len(selected_plans) > 0:
        with st.spinner("Analyzing plans..."):
            # Prepare prompt with plan details
            plan_details = []
            for plan in selected_plans:
                try:
                    details = read_plan_details(plan)
                    plan_details.append(f'<plan name="{plan}">{details}</plan>')
                except Exception as e:
                    st.error(f"Error reading details for plan '{plan}': {str(e)}")
                    continue
            
            if not plan_details:
                st.error("Unable to read details for any of the selected plans.")
                return

            prompt = f"{question}\n\n{''.join(plan_details)}"
            
            # Call AI21 API
            response = call_ai21_api(prompt)
            
            if response:
                try:
                    # Extract the message content from the nested structure
                    if 'choices' in response and len(response['choices']) > 0:
                        message = response['choices'][0]['message']['content']
                    else:
                        message = str(response)  # Fallback: convert the entire response to string
                    
                    st.subheader("Model Response:")
                    st.write(message)
                    
                    # Add button to view full response JSON
                    with st.expander('View Full Response'):
                        st.json(response)
                    
                except KeyError as e:
                    st.error(f"Failed to parse response: {e}")
                    st.json(response)
            else:
                st.error("No response from Jamba-1.5-Large.")
        st.success('Comparison complete!')
    
    st.markdown("---")
    st.write("Note: This app uses the Jamba-1.5-Large model to analyze insurance plans. The app makes a single call to Jamba with concatenated plan details for efficient comparison.")

if __name__ == "__main__":
    main()