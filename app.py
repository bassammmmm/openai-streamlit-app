import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from PyPDF2 import PdfReader
import pandas as pd
import openai
import os
from dotenv import load_dotenv


# Sidebar contents
with st.sidebar:
    st.title("AI-powered assistant")
    st.markdown('''
        ## About 
                This app is LLM-powered Chatbot
                **Tech Stack**
                OpenAI models
                StreamLit
        ''')
    add_vertical_space(15)

# Generate an answer using ChatGPT
def generate_answer(api_key, query):
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return response.choices[0].message.content

# Process the uploaded file (PDF or CSV)
def process_file(file, file_type):
    if file_type == 'pdf':
        text = ""
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file_type == 'csv':
        df = pd.read_csv(file)
        return df.to_string(index=False)  # Convert dataframe to a string for simplicity

def main():
    st.write("Chat with the PDF or Excel!")

    # OpenAI API key
    load_dotenv()
    api_key = st.secrets['OPENAI_API_KEY']
    if not api_key:
        api_key = os.environ.get('OPENAI_API_KEY')
    print(api_key)
    # Upload the file (PDF or CSV)
    file = st.file_uploader("Upload Your File", type=['pdf', 'csv'])

    if file:
        print(file.type)
        file_type = 'pdf' if file.type == 'application/pdf' else 'csv'
        file_text = process_file(file, file_type)

        # Making a query using file content
        query = st.text_input("Ask questions about the file.")
        if query:
            # Using the file content in the query
            new_query = f"Based on ({file_text}) content. {query}"
            response = generate_answer(api_key, query=new_query)
            st.write(response)

if __name__ == '__main__':
    main()
