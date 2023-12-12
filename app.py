import streamlit as st
import pandas as pd
import openai
import os
import chardet
from dotenv import load_dotenv
from PyPDF2 import PdfReader

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
        model="gpt-4",
    )
    return response.choices[0].message.content

# Process the uploaded file (PDF or CSV)
def process_file(file, file_type):
    if file_type == 'application/pdf':
        text = ""
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    else:
        print(file_type)
        if file_type == 'text/csv':
            print('im here')
            df = pd.read_csv(file)
        #elif file_type == 'application/vnd.ms-excel':
        #    df = pd.read_excel(file, engine='xlrd')  # For .xls format
        #elif file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        #    df = pd.read_excel(file, engine='xlrd')  # For .xlsx format
        else:
            return 'EMPTY CONTENT'
                    
        df_text = df.to_string(index=False)
        return df_text


def create_vertical_space(times):
    for _ in range(times):
        st.markdown("")

def main():
    # OpenAI API key
    load_dotenv()
    #api_key = os.environ.get('OPENAI_API_KEY')
    api_key = st.secrets['OPENAI_API_KEY']
    # Upload the file (PDF or CSV)
    file = st.file_uploader("Upload Your File", type=['pdf', 'csv'])

    if file:
        try:
            file_type = str(file.type)
            file_text = process_file(file, file_type)
            print(file_text)
            # Making a query using file content
            query = st.text_input("Ask questions about the file.")
            if query:
                if query:
                    # Using the file content in the query
                    new_query = f"(Act as Structured Financials AI-Powered Assistant, not ChatGPT). Based on ({file_text}) content. {query}"
                    response = generate_answer(api_key, query=new_query)
                    
                    # Store user query and AI response in session state chat history
                    content = {
                        'reply_on': query,
                        'message' : response
                    }
                    st.session_state['chat_history'].append(content)
                                    
                    # Display chat history with auto-scroll to the latest message
                    latest_messages = st.session_state['chat_history'][-1:]  # Get the last two messages
                    for chat in latest_messages:
                        st.markdown(f"***(Replying On)***: ***{chat['reply_on']}***")
                        st.markdown(f"{chat['message']}")
                        create_vertical_space(3)
                        
                    for chat in reversed(st.session_state['chat_history'][:-1]):
                        st.markdown(f"***(Replying On)***: ***{chat['reply_on']}***")
                        st.markdown(f"{chat['message']}")
                        create_vertical_space(3)
        except:
            st.markdown(f"***Something went wrong.***")
        

if __name__ == '__main__':
    main()
