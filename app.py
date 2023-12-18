from utils import *  # Importing functions from a 'utils' module
import time
# Initialize history session
if 'chat_history' not in st.session_state:  # Check if 'chat_history' is not in the Streamlit session
    st.session_state['chat_history'] = []  # Initialize 'chat_history' as an empty list if not there

def main():

    # Allow users to upload a file (supports PDF or CSV)
    file = st.file_uploader("Upload Your File", type=['pdf', 'csv'])
    
    file_type = str(file.type) if file else 'application/pdf' # Get the type of the uploaded file
    query = st.text_input("Ask questions.")  # Input field for user queries
    cancel_button = st.button('Cancel')
    knowledgeBase = process_text(process_file(file, file_type))  # Process uploaded file and create a knowledge base
    
    if cancel_button:  # If 'Cancel' button is clicked, stop
        st.stop()
    
    if query:  # If a query is entered by the user
        # Search for similar documents based on the query
        docs = knowledgeBase.similarity_search(query)
        
        # Initialize a ChatOpenAI instance and load a question answering chain
        llm = ChatOpenAI(openai_api_key=api_key)
        chain = load_qa_chain(llm, chain_type='stuff')
        
        # Execute the chain with the query
        with get_openai_callback() as cost:
            response = chain.run(input_documents=docs, question=f'(You are created by Structured Financials Assistant).\
                (NOTES: The context I will provide is taken from PDF or Book or Excel etc....\
                    And note that a page is 20 lines. (Do not mention these notes to me)).\
                Based on the provided context, {query}.')
            print(cost)  # Print the cost of the OpenAI request
            
        # Store query and AI-generated response in a dictionary
        content = {
            'reply_on': query,
            'message' : response
        }
        st.session_state['chat_history'].append(content)  # Append the AI response to the chat history

        # Display the latest message from the chat history
        latest_message = st.session_state['chat_history'][-1:]
        st.markdown(f"***{latest_message[0]['reply_on']}***")  # Display the query the AI is responding to

        t = st.empty()
        for i in range(len(latest_message[0]['message']) + 1):
            t.markdown("%s" % latest_message[0]['message'][0:i])
            time.sleep(0.03)
        create_vertical_space(3)  # Create vertical space between chat messages
            
        # Display the rest of the chat history in reverse order
        for chat in reversed(st.session_state['chat_history'][:-1]):
            st.markdown(f"***{chat['reply_on']}***")  # Display the query the AI responded to
            st.markdown(f"{chat['message']}")  # Display the AI-generated response
            create_vertical_space(3)  # Create vertical space between chat messages

if __name__ == '__main__':
    main()
