from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from rag_pipeline import get_chat_response
import os 
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # Allow cross-origin requests for development

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get JSON data from the request
        data = request.get_json()
        print(f"Received data: {data}")  # Debug line to check the request

        query = data.get("message")
        session_id = data.get("session_id", "default")

        if not query:
            return jsonify({"error": "No query provided"}), 400

        # Process the message (assuming `get_chat_response` handles it)
        response = get_chat_response(query, session_id=session_id)
        return jsonify({"response": response})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

