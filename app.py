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

# Simplified function to read plan details from file
def read_plan_details(plan_name):
    file_path = os.path.join('data', f"{plan_name}.txt")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        raise ValueError(f"Unable to read file {file_path} with UTF-8 encoding.")

# Function to call AI21 API (Jamba)
def call_ai21_api(prompt):
    if 'AI21_API_KEY' not in st.secrets:
        st.error("AI21 API key not found in Streamlit secrets.")
        return None

    api_key = st.secrets['AI21_API_KEY']
    url = 'https://api.ai21.com/studio/v1/j2-jumbo-instruct/complete'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "prompt": prompt,
        "numResults": 1,
        "maxTokens": 5000,
        "temperature": 0.3,
        "topKReturn": 0,
        "topP": 1,
        "countPenalty": {
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        "frequencyPenalty": {
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        "presencePenalty": {
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        "stopSequences": []
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
    st.title("Insurance Plan Comparison with AI21 Jamba")

    st.write("""
    Welcome to the Insurance Plan Comparison App! This tool empowers you to compare various healthcare plans using detailed plan information loaded from local files. With the help of the AI21 Jamba model, you can pose specific questions to guide your decision-making process.
    """)

    # Get all available plans
    all_plans = get_insurance_plans()

    # Allow user to select up to 2 plans
    selected_plans = st.multiselect("Select up to 2 plans to compare:", all_plans, max_selections=2)

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

    # Text input for user's question
    if selected_question == "Custom question":
        question = st.text_input("Enter your custom question about the selected plans:")
    else:
        question = st.text_input("Question about the selected plans:", value=selected_question)

    # Button to run the comparison
    if st.button('Compare Plans') and len(selected_plans) > 0:
        with st.spinner("Analyzing plans..."):
            # Prepare prompt with plan details
            plan_details = []
            for plan in selected_plans:
                try:
                    details = read_plan_details(plan)
                    plan_details.append(f"Plan: {plan}\nDetails: {details}\n")
                except ValueError as e:
                    st.error(str(e))
                    continue
            
            if not plan_details:
                st.error("Unable to read details for any of the selected plans.")
                return

            prompt = f"Question: {question}\n\nPlan Information:\n{''.join(plan_details)}\nPlease compare these plans and answer the question."
            
            # Call AI21 API
            response = call_ai21_api(prompt)
            
            if response:
                try:
                    # Extract the message content from the nested structure
                    if 'completions' in response and len(response['completions']) > 0:
                        message = response['completions'][0]['data']['text']
                        st.subheader("AI Response:")
                        st.write(message)
                    else:
                        st.error("Unexpected response structure from AI21 API")
                    
                    # Add button to view full response JSON
                    with st.expander('View Full API Response'):
                        st.json(response)
                    
                except KeyError as e:
                    st.error(f"Failed to parse response: {e}")
                    st.json(response)
            else:
                st.error("No response from AI21 API.")
        st.success('Comparison complete!')

if __name__ == "__main__":
    main()