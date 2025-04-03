# Sea Level Rise Chat Assistant
[The app can be accessed here](https://sea-level-rise-ai-assistant.streamlit.app/)

# Problem Statement
The City of Arcata is developing a sea level rise strategy in its draft Local Coastal Program and in 2018 it commissioned a study on sea level rise. Combined, the draft Local Coastal Program and the 2018 sea level rise study are 171 pages of dense scientific and burecreatif language that can mistify more than enlighten. This discourages participation and input on Arcata's sea level rise strategy from community members. 

# Features
The Sea Level Rise Assistant is a chatbot which can answer questions about sea level rise policy and research specific to Arcata, California.

# Tech Stack
**OpenAI Assistants API**
Utilized to build a structured, persistent chatbot with context-aware capabilities, based on GPT-3.5. The API allows for managing threads, messages, and assistant behavior over time.

**OpenAI Python SDK**
Used to interface with the Assistants API, enabling integration of GPT-3.5 into the backend. Handles communication between the chatbot logic and the language model.

**File Search Tool (via Assistants API)**
Documents are pre-uploaded and made searchable by the Assistant. This allows the chatbot to answer questions about sea level rise using trusted PDFs and datasets without requiring users to upload or input document content manually.

**Streamlit**
A Python-based web app framework used to build the chatbot’s front-end:
* Provides a clean, interactive chat interface.
* Supports free hosting via Streamlit Community Cloud for public access.

# Installation 
1. Clone the repo 
   * In your terminal, go to the folder you want to use for your project and use the following commands 
        git clone https://github.com/yourusername/job-app-assistant.git
        cd job-app-assistant 
        pip install -r requirements.txt

2. Manage OpenAI API
   * Create an account with OpenAI 
   * Purchase credits
   * Create an API key by going to this page: https://platform.openai.com/settings/organization/api-keys
   * In your own cloned repo, create a file called .env and put in the following (without the quotes, replacing the fake key with your own API key string) "OPENAI_API_KEY=my-key-123"
   * If you plan to host your own project on github, make sure to add the .env to your .gitignore

3. Install dependencies with the terminal command: pip install -r requirements.txt

4. Uncomment code in main.py
   * Some of the code in main.py is used only once to create the assistant, create a vector store, and attach documents to the vector store. This is currently commented out in main(). When you first run your program, you should uncomment these calls, then HARDCODE the assistant_id and comment out the code again. After that, you will be able to have multiple chats with the assistant.

5. Run the app on http://localhost:8501/ with the terminal command: streamlit run main.py

6. Optional: Create a free account with [Streamlit Community Cloud] (https://streamlit.io/cloud) to host on a url


# Acknowledgements
Thanks to Free Code Camp for their video "OpenAI Assistants API – Course for Beginners".

