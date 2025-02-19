from dotenv import load_dotenv
import openai
import time
import logging
import streamlit as st

# manage the API secret key
load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]

def upload_files(client, filepaths):
    """
    Uploads multiple documents to API files endpoint, returns an array of the file ids
    and prints a confirmation message with the # of files that were uploaded.

    :param client: instance of the OpenAI API
    :param filepaths: array of the filepaths for the files to upload
    :return: file_ids: array of the file ids for the files that were uploaded
    """

    file_ids = []
    count = 0
    for path in filepaths:
        file = client.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )
        file_ids.append(file.id)
        count +=1
    print(f"{count} file(s) uploaded")
    return file_ids


def create_vector_store(client, vector_store_name):
    """
    Creates a new vector store which is accessible by the AI Assistant's file
    search tool. Returns the vector store's ID as a string.

    :param client: instance of the OpenAI API
    :param vector_store_name: string, desired name of the vector store
    :return: vector_store.id: string, id of the newly created vector store
    """

    vector_store = client.beta.vector_stores.create(name=vector_store_name)
    print(f"{vector_store_name} vector store was created with ID: {vector_store.id}")
    return vector_store.id


def attach_file_to_vector_store(client, vector_store_id, file_ids):
    """
    Attaches files to vector store. This is OpenAI API's way for the GPT to read the files.
    Prints a confirmation with a count of hte number of files added to the vector store.

    :param client:  instance of the OpenAI API
    :param vector_store_id: string, id of the vector store
    :param file_ids: array of strings, ids of the files
    :return: None
    """
    count = 0
    for file_id in file_ids:
        client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
        count += 1
    print(f"{count} file(s) added to vector store")


def create_assistant(client, assistant_name, instructions, vector_store_id, model):
    """
    Creates a new assistant with capability to use the file search tool.

    :param client: instance of the OpenAI API
    :param assistant_name: string, desired name of the Assistant
    :param instructions: string, detailed instructions for Assistant's persona, tone, and way it should
                         respond to prompts (Ex. You are a Michellin star chef who gives advice...)
    :param vector_store_id: string, id of the vector store to associate with the Assistant
    :param model: string, alias of the GPT model (Ex. GPT-4o)
                  Full list of aliases: https://platform.openai.com/docs/models/gpt-4#current-model-aliases
    :return: assistant.id: string, id for the newly created Assistant
    """

    assistant = client.beta.assistants.create(
        name=assistant_name,
        instructions=instructions,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        model=model,
    )

    print(f"{assistant_name} was created with ID: {assistant.id}")
    return assistant.id


def create_thread(client):
    """
    Creates a thread. OpenAI's API documentation describe a thread as 'a conversation session
    between an Assistant and a user. Threads store Messages.'

    :param client: instance of the OpenAI API
    :return: thread.id: string, id of the newly created thread
    """

    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")
    return thread.id


def add_user_message_to_thread(client, thread_id, message):
    """
    Appends the user message to the thread so the Assistant has access to the content.
    Otherwise, no action is taken. The AI will generate a response in a later step.

    :param client: instance of the OpenAI API
    :param thread_id: string, id of the thread, which is one conversation session between Assistant and user
    :param message: string, the content of the user's prompt or message
    :return: None
    """

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )


def create_run(client, thread_id, assistant_id):
    """
    Creates a run which OpenAI API documentation describes as 'an invocation of an Assistant on a Thread...
    As part of a Run, the Assistant appends [its own] Messages to the Thread.'

    Note: While needing to create a run in order to produce a response from the AI seems like an unnecessary 
          extra step, it allows for more options. For example, see that you need to specify the assistant_id-- 
          you can actually have several assistants chiming into one conversation by changing the assistant_id 
          that is specified for each run.

    :param client: instance of the OpenAI API
    :param thread_id: string, id of the thread, which is one conversation session between Assistant and user
    :param assistant_id: string, id of the Assistant whose response is desired
    :return: run_id: string, id of the run action
    """

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    return run.id


def retrieve_assistant_response(client, thread_id, run_id):
    """
    Waits for a run to complete and prints the elapsed time and the assistant's message.

    :param client: instance of the OpenAI API
    :param thread_id: string, id of the current thread
    :param run_id: string, id of the latest run
    :return: response: string, content of the AI Assistant's response.
    """

    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages once run is complete
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                return response
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(5)


def main():

    # Create an OpenAI client instance that uses the API key from environment variables
    client = openai.OpenAI()

    # =======================Code used one time to upload files to API endpoint and create Assistant==================

    # 1. Upload files to the files endpoint and get file IDs
    # filepaths = [os.path.join("documents", "City_of_Arcata_Sea_Level_Rise_Vulnerability_Assessment.pdf"),
    #              os.path.join("documents", "City_of_Arcata_LCP_Update_DRAFT.pdf")]
    # file_ids = upload_files(client, filepaths)

    # 2. Create a vector store and get the vector store ID
    # vector_store_id = create_vector_store(client, "Sea Level Rise Documents")

    # 3. Attach the files to the vector store
    # attach_file_to_vector_store(client, vector_store_id, file_ids)

    # 4. Create an assistant and attach the vector store to the assistant
    # assistant_id = create_assistant(client,
    #                                 "Sea Level Rise Arcata Assistant",
    #                                 """You are a neutral third-party with knowledge of key policy, grants,
    #                                 and studies related to sea level rise in the City of Arcata in Humboldt County,
    #                                 California. Speak tersely. As much as possible, cite and quote from documents to
    #                                 support your answers.""",
    #                                 vector_store_id,
    #                                 "gpt-3.5-turbo-0125")
    assistant_id = 'asst_mmc1upNxaYhajQbTgKo0XwMr'

    # =======================Optional code: for chatting with assistant within the IDE==================

    # 5. Create a thread
    # thread_id = create_thread()

    # 7. Create a message in the thread
    # create_message(thread_id, """Please summarize Arcata's Sea Level Rise policy in
    # the draft Local Coastal Program Update.""")

    # 8. Create a run on the thread
    # run_id = create_run(thread_id, assistant_id)

    # 9. Retrieve run information
    # retrieve_assistant_response(thread_id, run_id)

    # ====================================STREAMLIT APP====================================

    st.set_page_config(page_title="Sea Level Rise Assistant", page_icon="🌊")

    st.title("🌊 Sea Level Rise Assistant")

    st.write(
        "Hello! I’m a chatbot powered by OpenAI’s GPT-3.5. I can answer questions about sea level rise in Arcata, "
        "using information from the *City of Arcata’s 2018 Sea Level Rise Vulnerability Assessment* and the *City of "
        "Arcata’s 2023 Draft Local Coastal Program Update.* "
        "Feel free to ask me about these documents or sea level rise in Arcata in general.  \n\n"
        "**Note:** While I strive to provide accurate information, please verify details by reviewing the reports or "
        "consulting City staff directly."
    )

    # Streamlit's Session State: a dictionary like-object which tracks user action's on the page.
    # Every user event causes the app to refresh and run the code from the top. When it refreshes,
    # it looks at session state to track chat history and other user events.

    # Initialize Streamlit session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread" not in st.session_state:
        st.session_state.thread = create_thread(client)

    # displays chat messages from session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # takes in user's chat input
    user_message = st.chat_input("Hi! Ask me about sea level rise in Arcata, California.")
    # if the user's input is not empty
    if user_message:
        # adds user message to session state
        st.session_state.messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)

        # sends user's message to OpenAI Assistant API
        # a thread is OpenAI's way of keeping track of messages in one conversation
        add_user_message_to_thread(client, st.session_state.thread, user_message)

        # create a run, which will produce Assistant's response
        run_id = create_run(client, st.session_state.thread, assistant_id)

        # retrieve and store Assistant's response
        reply_content = retrieve_assistant_response(client, st.session_state.thread, run_id)

        # Add assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": reply_content})
        with st.chat_message("assistant"):
            st.markdown(reply_content)

    # Run app on http://localhost:8501/ with the terminal command: streamlit run main.py

if __name__ == '__main__':
    main()
