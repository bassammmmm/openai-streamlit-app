import streamlit as st
import pandas as pd
import openai
import os
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        model="gpt-3.5-turbo",
    )
    return response.choices[0].message.content

def process_page(page, total_pages, api_key, query):
    text = f'As Structured Financials AI-Powered Assistant. Based on:{page.extract_text()}.\
            {query}'
    return generate_answer(api_key, query=text)

def process_file(file, file_type, query):
    load_dotenv()
    api_key = os.environ.get('OPENAI_API_KEY')
    response = ""

    if file_type == 'application/pdf':
        pdf_reader = PdfReader(file)
        total = len(pdf_reader.pages)

        with st.spinner(f'Digging deep into your {total} page(s)... ETA'):

            with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust `max_workers` as needed
                future_to_page = {
                executor.submit(process_page, page, total, api_key, query): page
                for page in pdf_reader.pages
            }

            for future in as_completed(future_to_page):
                response += future.result() + "\n"
                
        return response
    
    elif file_type == 'text/csv':
        chunksize = 20000  # Number of rows to process together
        df_chunks = pd.read_csv(file, encoding='utf-8', chunksize=chunksize)
        response = ""
        with st.spinner('Digging deep into your rows... (This may take time)') as spin:
            for index, chunk in enumerate(df_chunks):
                chunk_text = ""  # To accumulate text for this chunk
                print(chunk)
                chunk_text += f'As Structured Financials AI-Powered Assistant, not ChatGPT. Based on:{chunk} (This is only a part of the data.). {query}' + '\n'  # Accumulate text for this chunk
                # Generate answer for the accumulated chunk text
                response += generate_answer(api_key, query=chunk_text) + "\n"
                print(response)
        return response

    else:
        return st.write('Something went wrong.')


import os
import multiprocessing



def create_vertical_space(times):
    for _ in range(times):
        st.markdown("")

def main():
    # OpenAI API key

    def get_processor_info():
        num_cores = os.cpu_count()  # Get the number of logical CPU cores
        

        
        return num_cores

    num_cores = get_processor_info()
    print(f"Number of CPU cores: {num_cores}")


    # Upload the file (PDF or CSV)
    file = st.file_uploader("Upload Your File", type=['pdf', 'csv'])
    if file:
        file_type = str(file.type)
        
        #print(file_text)
        # Making a query using file content
        query = st.text_input("Ask questions about the file.")
        if query:
            # Using the file content in the query
            #new_query = f"(Act as Structured Financials AI-Powered Assistant, not ChatGPT). Based on ({file_text}) content. {query}"
            #response = generate_answer(api_key, query=new_query)
            response = process_file(file, file_type, query)
            # Store user query and AI response in session state chat history
            content = {
                'reply_on': query,
                'message' : response
            }
            st.session_state['chat_history'].append(content)
                            

            latest_messages = st.session_state['chat_history'][-1:]  # Getting the last message
            for chat in latest_messages:
                st.markdown(f"***(Replying On)***: ***{chat['reply_on']}***")
                st.markdown(f"{chat['message']}")
                create_vertical_space(3)
                
            for chat in reversed(st.session_state['chat_history'][:-1]): #The rest of the messages
                st.markdown(f"***(Replying On)***: ***{chat['reply_on']}***")
                st.markdown(f"{chat['message']}")
                create_vertical_space(3)

        

if __name__ == '__main__':
    main()
