import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from PyPDF2 import PdfReader


from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI

load_dotenv()

#First line should be executed for testing locally, second line is for production
#api_key = os.environ.get('OPENAI_API_KEY')
api_key = st.secrets['OPENAI_API_KEY']


# Function to process different types of files
def process_file(file, file_type):
    try:
        if file_type == 'application/pdf':  # For PDF files
            pdf_reader = PdfReader(file)  # Read PDF file
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text  # Return the file text
        
        elif file_type == 'text/csv':  # For CSV files
            df = pd.read_csv(file, encoding='utf-8')  # Read CSV 
            return df.to_string(index=False)  # Return the file text

        else: 
            return st.write('Something went wrong.')  # Display an error message
    except:
        text = 'No content'
        return text
    
# Function to process text and generate a knowledge base
def process_text(text):
    # Split the text into chunks using Langchain's CharacterTextSplitter
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    # Convert the chunks of text into embeddings to form a knowledge base
    embeddings = OpenAIEmbeddings()
    knowledgeBase = FAISS.from_texts(chunks, embeddings)
    
    return knowledgeBase

# Function to create vertical space in Streamlit app
def create_vertical_space(times):
    """Creates vertical space in the Streamlit app."""
    for _ in range(times): 
        st.markdown("")  # Add empty space
