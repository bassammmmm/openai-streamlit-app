import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import openai
import os
from dotenv import load_dotenv

# Initialize history session
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

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
    # OpenAI API key
    load_dotenv()
    #api_key = os.environ.get('OPENAI_API_KEY')
    api_key = st.secrets['OPENAI_API_KEY']
    # Upload the file (PDF or CSV)
    file = st.file_uploader("Upload Your File", type=['pdf', 'csv'])

    if file:
        try:
            file_type = 'pdf' if file.type == 'application/pdf' else 'csv'
            file_text = process_file(file, file_type)

            # Making a query using file content
            query = st.text_input("Ask questions about the file.")
            if query:
                if query:
                    # Using the file content in the query
                    new_query = f"(Act as Structured Financials AI-Powered Assistant, not ChatGPT). Based on ({file_text}) content. {query}"
                    response = generate_answer(api_key, query=new_query)
                    
                    # Store user query and AI response in session state chat history
                    st.session_state['chat_history'].append({"role": "AI", "content": response})
                    st.session_state['chat_history'].append({"role": "You", "content": query})
                    

                    # Display chat history with auto-scroll to the latest message
                    latest_messages = st.session_state['chat_history'][-2:]  # Get the last two messages
                    for chat in latest_messages:
                        st.write(f"{chat['role']}: {chat['content']}")

                    for chat in st.session_state['chat_history'][:-2]:
                        st.write(f"{chat['role']}: {chat['content']}")
        except:
            st.write('Something went wrong.')

if __name__ == '__main__':
    main()
