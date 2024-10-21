import streamlit as st
import pandas as pd
import json
from ai21 import AI21Client

def main():
    st.title("Basic Streamlit App")
    
    st.write("This is a basic Streamlit app that imports pandas, json, and ai21.")
    
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
    
    # Example using ai21 (Note: You'll need to set up your AI21 API key)
    st.write("AI21 Integration:")
    st.write("To use AI21, you need to set up your API key. Here's a placeholder for AI21 functionality.")
    
    # Placeholder for AI21 functionality
    if st.button("Generate Text with AI21"):
        st.write("AI21 text generation would happen here. Make sure to set up your API key!")

if __name__ == "__main__":
    main()
