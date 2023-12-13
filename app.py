from utils import *

# Initialize history session
if 'chat_history' not in st.session_state:  # Check if 'chat_history' is not in the Streamlit session state
    st.session_state['chat_history'] = []  # Initialize 'chat_history' as an empty list if not present

def main():
    # Allow users to upload a file (supports PDF or CSV)
    file = st.file_uploader("Upload Your File", type=['pdf', 'csv'])
    
    if file:  # If a file is uploaded
        
        file_type = str(file.type)  # Get the type of the uploaded file
        query = st.text_input("Ask questions about the file.")  # Input field for user queries
        
        if query:  # If a query is entered by the user

            response = process_file(file, file_type, query)  # Process the uploaded file based on its type and the query entered

            content = {
                'reply_on': query,  # Store the query to which the AI responds
                'message' : response  # Store the AI-generated response
            }
            st.session_state['chat_history'].append(content)  # Append the AI response to the chat history

            latest_message = st.session_state['chat_history'][-1:]  # Get the latest message from the chat history
            st.markdown(f"***(Replying On)***: ***{latest_message[0]['reply_on']}***")  # Display the query the AI is responding to
            st.markdown(f"{latest_message[0]['message']}")  # Display the AI-generated response
            create_vertical_space(3)  # Create vertical space between chat messages
                
            for chat in reversed(st.session_state['chat_history'][:-1]):  # Iterate over the rest of the chat history in reverse order
                st.markdown(f"***(Replying On)***: ***{chat['reply_on']}***")  # Display the query the AI responded to
                st.markdown(f"{chat['message']}")  # Display the AI-generated response
                create_vertical_space(3)  # Create vertical space between chat messages

if __name__ == '__main__':
    main()