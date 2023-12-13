import streamlit as st
import pandas as pd
import openai
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Generate an answer using ChatGPT
def generate_answer(api_key, query):
    """Generates an answer using the OpenAI GPT-3 API."""
    client = openai.OpenAI(api_key=api_key)  # Initialize OpenAI client
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,  # Query to be sent
            }
        ],
        model="gpt-3.5-turbo",  # Use GPT-3.5-turbo model
    )
    return response.choices[0].message.content  # Return the generated response

def process_page(page, api_key, query):
    """Gets a response for an individual page of a PDF."""
    text = f'As Structured Financials AI-Powered Assistant. Based on:{page.extract_text()}. {query}'  # Extracted text from the page
    return generate_answer(api_key, query=text) + "\n"  # Return generated response for the page

def process_chunk(chunk, api_key, query):
    """Gets a response for an chunk of an Excel file."""
    chunk_text = f'As Structured Financials AI-Powered Assistant. Based on:{chunk}.{query}'  # Chunk of data from CSV
    return generate_answer(api_key, query=chunk_text) + "\n"  # Return generated response for the chunk

def process_file(file, file_type, query):
    """Processes the uploaded file based on its type (PDF or CSV)."""
    load_dotenv()  # Load environment variables
    api_key = os.environ.get('OPENAI_API_KEY')  # Get OpenAI API key from environment
    response = ""  # Initialize response variable

    if file_type == 'application/pdf':  # For PDF files
        pdf_reader = PdfReader(file)  # Read PDF file
        pages_length = len(pdf_reader.pages)  # Get number of pages
        time_per_page = 3.46  # Estimated time per page processing

        eta_seconds = pages_length * time_per_page  # Calculate total processing time
        eta_minutes, eta_seconds = divmod(eta_seconds, 60)  # Convert processing time to minutes and seconds
        
        # Create an ETA message based on the number of pages
        message = f'Digging deep into your {pages_length} page(s)... ETA {int(eta_minutes)} minute(s) and {int(eta_seconds)} second(s).' if not int(eta_minutes) == 0 else f'Digging deep into your {pages_length} page(s)... ETA {int(eta_seconds)} second(s).'
                    
        with st.spinner(message):  # Display ETA in Streamlit spinner
            with ThreadPoolExecutor(max_workers=5) as executor:  # Use ThreadPoolExecutor for concurrent processing
                # Process each page concurrently
                future_to_page = {
                    executor.submit(process_page, page, api_key, query): page
                    for page in pdf_reader.pages
                }

                for future in as_completed(future_to_page):  # As each future is completed
                    response += future.result() + "\n"  # Add the result to the response
                
        return response  # Return the accumulated response
    
    elif file_type == 'text/csv':  # For CSV files
        chunksize = 30000  # Define chunk size for reading CSV
        df_chunks = pd.read_csv(file, encoding='utf-8', chunksize=chunksize)  # Read CSV in chunks

        with st.spinner('Digging deep into your rows... ') as spin:  # Display message in Streamlit spinner
            with ThreadPoolExecutor(max_workers=5) as executor:  # Use ThreadPoolExecutor for concurrent processing
                # Process each chunk of the CSV concurrently
                futures = {executor.submit(process_chunk, chunk, api_key, query): chunk for chunk in df_chunks}
                for future in as_completed(futures):  # As each future is completed
                    response += future.result()  # Add the result to the response

        return response  # Return the accumulated response

    else:  # If file type is not supported
        return st.write('Something went wrong.')  # Display an error message

def create_vertical_space(times):
    """Creates vertical space in the Streamlit app."""
    for _ in range(times):  # Loop for specified number of times
        st.markdown("")  # Add empty space
