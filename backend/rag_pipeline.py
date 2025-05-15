# rag_pipeline.py

import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings, ChatCohere

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Constants
FAISS_DB_PATH = "vectorstore"
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Load embedding model
embedding_model = CohereEmbeddings(model="embed-english-v3.0")

# Load vectorstore
faiss_db = FAISS.load_local(
    FAISS_DB_PATH,
    embedding_model,
    allow_dangerous_deserialization=True
)

# Load Cohere chat model
llm_model = ChatCohere(
    model="command-r-plus",
    temperature=0.3
)

# Prompt template (🆕 Updated for HTML formatting)
custom_prompt_template = """
You are a helpful assistant for Xalt Analytics.
 
Your task is to answer the user's question in a clear, clean, and readable HTML format.
Always format your answers using HTML tags such as:
- <p> for paragraphs
- <ul><li> or <ol><li> for lists
- <a href="..."> for clickable links (for email, phone, or URLs)
- <strong> for emphasis
 
ONLY respond with specific company information (emails, phone numbers, consultation link, timings, etc.) IF the user explicitly asks for it.
 
Guidelines:
- For sales-related emails, use: <a href="mailto:sales@xaltanalytics.com">sales@xaltanalytics.com</a>
- For career-related emails, use: <a href="mailto:careers@xaltanalytics.com">careers@xaltanalytics.com</a>
- For phone/contact number, use: <a href="tel:7225020264">7225020264</a> and <a href="tel:9302594888">9302594888</a>
- For consultation, suggest this link: <a href="https://calendly.com/suvi-pandey-xaltanalytics/30min?month=2025-05">Book a consultation</a>
- For office hours: Monday to Friday, 9 AM to 6:30 PM
 
NEVER reveal any company details unless the user's query specifically asks for them.
 
If the user greets you (e.g., "Hi", "Hello"), respond politely and ask how you can assist them — but DO NOT provide company details until asked.
 
If the user's question is unrelated to Xalt Analytics or outside the context provided (e.g., about public figures, general knowledge, or unrelated services), respond with the following polite message in HTML:
 
<p>I'm here to assist you with queries specifically related to Xalt Analytics and its services. For anything outside this scope, I'm unable to provide information. Please feel free to ask anything about our offerings, consultations, or business details.</p>
 
Chat History:
{history}
 
Relevant Context:
{context}
 
User Question:
{question}
 
HTML Response:
"""


# Retrieve documents
def retrieve_docs(query):
    return faiss_db.similarity_search(query)

# Extract context from docs
def get_context(documents):
    return "\n\n".join([doc.page_content for doc in documents])

# Memory store per session
chat_memory_store = {}

def get_memory(session_id):
    if session_id not in chat_memory_store:
        chat_memory_store[session_id] = InMemoryChatMessageHistory()
    return chat_memory_store[session_id]

# 🧠 MAIN FUNCTION FOR BACKEND USAGE
def get_chat_response(user_input, session_id="default"):
    memory = get_memory(session_id)
    
    # Step 1: Retrieve context
    docs = retrieve_docs(user_input)
    context = get_context(docs)
    
    # Step 2: Build chain with history
    prompt = ChatPromptTemplate.from_template(custom_prompt_template)
    chain = prompt | llm_model

    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: memory,
        input_messages_key="question",
        history_messages_key="history"
    )

    # Step 3: Get response
    response = chain_with_history.invoke(
        {"question": user_input, "context": context},
        config={"configurable": {"session_id": session_id}}
    )

    # Step 4: Save to memory
    memory.add_message(HumanMessage(content=user_input))
    memory.add_message(AIMessage(content=response.content))

    return response.content
