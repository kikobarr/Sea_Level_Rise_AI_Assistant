import openai
import os
from dotenv import find_dotenv, load_dotenv
from pathlib import Path
from openai import OpenAI
import time
import logging
from datetime import datetime
import streamlit as st

load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]


def upload_files(client, filepaths):
    """Uploads multiple documents to files endpoint and returns the file ids."""

    uploaded_files = []
    count = 0
    for path in filepaths:
        file = client.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )
        uploaded_files.append(file.id)
        count +=1
    print(f"{count} file(s) uploaded")
    return uploaded_files


def create_vector_store(client, vector_store_name):
    """Creates a new vector store and returns the ID."""
    vector_store = client.beta.vector_stores.create(name=vector_store_name)
    print(f"{vector_store_name} vector store was created with ID: {vector_store.id}")
    return vector_store.id


def attach_file_to_vector_store(client, vector_store_id, file_ids):
    count = 0
    for file_id in file_ids:
        vector_store_file = client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
        count += 1
    print(f"{count} file(s) added to vector store")


def create_assistant(client, assistant_name, instructions, vector_store_id, model):
    """Creates a new assistant with capability to use the file search tool."""

    assistant = client.beta.assistants.create(
        name=assistant_name,
        instructions=instructions,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        model=model,
    )

    print(f"{assistant_name} was created with ID: {assistant.id}")
    return assistant.id


def create_thread(client):
    """Creates a thread. Threads are 'a conversation session between an Assistant and a user. Threads store Messages
    and automatically handle truncation to fit content into a model’s context.'"""
    # TODO: thread can also have a tool_resources with file_search with vector_store_ids... better to have the files
    #  embedded in the assistant or the thread? probably the assistant...
    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")
    return thread.id


def create_message(client, thread_id, message):

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

    #TODO: do I need to return anything?
    return message.id


def create_run(client, thread_id, assistant_id):
    """Creates a run. A run is 'an invocation of an Assistant on a Thread. The Assistant uses its configuration
    and the Thread’s Messages to perform tasks by calling models and tools. As part of a Run, the Assistant appends
    Messages to the Thread.'"""
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    return run.id


def retrieve_assistant_response(client, thread_id, run_id, sleep_interval=5):
    """Waits for a run to complete and prints the elapsed time and the assistant's message."""
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages once run is complete
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


def main():

    # 1. Create an instance of the OpenAI API
    client = OpenAI()

    # 2. Upload files to the files endpoint and get file IDs
    # filepath_1 = os.path.join("documents", "City_of_Arcata_Sea_Level_Rise_Vulnerability_Assessment.pdf")
    # filepath_2 = os.path.join("documents", "City_of_Arcata_LCP_Update_DRAFT.pdf")
    # filepaths = [filepath_1, filepath_2]
    # file_ids = upload_files(client, filepaths)

    # 3. Create a vector store and get the vector store ID
    # vector_store_id = create_vector_store(client, "Sea Level Rise Documents")

    # 4. Attach the files to the vector store
    # attach_file_to_vector_store(client, vector_store_id, file_ids)

    # 5. Create an assistant and attach the vector store to the assistant
    # assistant_id = create_assistant(client,
    #                                 "Sea Level Rise Arcata Assistant",
    #                                 """You are a neutral third-party with knowledge of key policy, grants,
    #                                 and studies related to sea level rise in the City of Arcata in Humboldt County,
    #                                 California. Speak tersely. As much as possible, cite and quote from documents to
    #                                 support your answers.""",
    #                                 vector_store_id,
    #                                 "gpt-3.5-turbo-0125",
    #                                 )
    assistant_id = 'asst_mmc1upNxaYhajQbTgKo0XwMr'

    # 6. Create a thread
    thread_id = create_thread(client)

    # 7. Create a message in the thread
    create_message(client, thread_id, """Please summarize Arcata's Sea Level Rise policy in 
    the draft Local Coastal Program Update.""")

    # 8. Create a run on the thread
    run_id = create_run(client, thread_id, assistant_id)

    # 9. Retrieve run information
    retrieve_assistant_response(client, thread_id, run_id)

# ====================================STREAMLIT APP====================================

    st.title("Sea Level Rise ChatBot")
    st.write("I am a chatbot that has pre-loaded with the City_of_Arcata_Sea_Level_Rise_Vulnerability_Assessment"
             "and City_of_Arcata_LCP_Update_DRAFT.")

    assistant_model = f"ft:gpt-3.5-turbo-0125:{assistant_id}"

    # session_state is "dictionary-like" and thread_id, messages, and runs are keys
    # initializes new session
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = [create_thread(client)]
        st.session_state.messages = []
        st.session_state.runs = []

    # Display chat messages from history on app rerun
    # Iterates over the messages list stored in st.session_state.
    # Each item in st.session_state.messages is a dictionary,
    #   {"role": "user", "content": "What is the weather like?"}
    #   {"role": "assistant", "content": "It is sunny with a high of 75°F."}
    for message in st.session_state.messages:
        # Creates a visual container in the app for displaying a message.
        with st.chat_message(message["role"]):
            # Displays the message's text inside the container created by st.chat_message.
            st.markdown(message["content"])

    # If a user's message is not empty, adds the message to the session_state.messages dictionary
    if user_message := st.chat_input("Hi! Ask me about sea level rise in Arcata, California."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_message})
        # Displays user message in chat message bubble
        with st.chat_message("user"):
            st.markdown(user_message)

        # user message  is appended
        # user message is appended to session state
        # message is passed to Assistant
        # run is executed
        # retrieve run info

    # with st.form(key="user_input_form"):
    #      instructions = st.text_input("Enter your question for the ChatBot")
    #      submit_button = st.form_submit_button(label="Run Assistant")
    #
    #      if submit_button:



if __name__ == '__main__':
    main()


# def get_vector_store_info(client):
#     """Prints list of existing vector stores and number of files for each."""
#
#     # creating a list of vector stores
#     existing_vector_stores = client.beta.vector_stores.list()
#
#     # Printing the name of each vector store
#     for store in existing_vector_stores.data:
#         print(f"Vector Store: {store.name} (ID: {store.id}) has {store.file_counts.total} file(s)")