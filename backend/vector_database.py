import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings  # Updated import for CohereEmbeddings
from langchain_community.vectorstores import FAISS  # Updated import for FAISS
import faiss

# Load environment variables
load_dotenv()

# Constants
TXT_DIRECTORY = 'txt/'
FILE_PATH = os.path.join(TXT_DIRECTORY, 'data_for_chatbot_xalt.txt')  # Path to your document
FAISS_DB_PATH = "vectorstore"  # Directory where FAISS index will be saved
COHERE_API_KEY = os.getenv("COHERE_API_KEY")  # Ensure the API key is loaded from .env

# Step 1: Load text file
def load_txt(file_path):
    loader = TextLoader(file_path, encoding='utf-8')
    return loader.load()

# Step 2: Split documents into chunks
def create_chunks(documents): 
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

# Step 3: Initialize Cohere embeddings
def get_embedding_model():
    return CohereEmbeddings(model="embed-english-v3.0")  # You can adjust to other models if needed

# Step 4: Create or update the FAISS vector database
def build_or_update_vector_db(new_file_path=None):
    print("📄 Loading and chunking documents...")
    documents = load_txt(new_file_path or FILE_PATH)
    text_chunks = create_chunks(documents)
    embedding_model = get_embedding_model()

    # Check if the FAISS vectorstore already exists
    if os.path.exists(FAISS_DB_PATH) and os.path.exists(os.path.join(FAISS_DB_PATH, "index.faiss")):
        print("🔄 Updating existing vector DB...")
        db = FAISS.load_local(
            FAISS_DB_PATH,
            embedding_model,
            allow_dangerous_deserialization=True
        )
        db.add_documents(text_chunks)
    else:
        print("🆕 Creating new vector DB...")
        db = FAISS.from_documents(text_chunks, embedding_model)

    # Save the FAISS vectorstore locally
    db.save_local(FAISS_DB_PATH)
    print(f"✅ Vector DB saved at: {FAISS_DB_PATH}")

# Only run if this script is executed directly
if __name__ == "__main__":
    build_or_update_vector_db()
