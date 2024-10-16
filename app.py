import json
import os
from flask import Flask, jsonify, request, send_file, send_from_directory
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Creates a Flask web application named app.
app = Flask(__name__)

# Set the Google API key
os.environ["GOOGLE_API_KEY"] =  os.getenv('GOOGLE_API_KEY')

# Initialize an empty list to keep track of request-response history
history = []

@app.route('/')
def home():
    return send_file('web/index.html')

@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        try:
            req_body = request.get_json()
            content = req_body.get("contents")
            model_name = req_body.get("model")

            # Append the user's request to the history
            history.append({"role": "user", "content": content})

            # Create the model
            model = ChatGoogleGenerativeAI(model=model_name)

            # Convert the history into HumanMessage objects for the model
            messages = [HumanMessage(content=item["content"]) for item in history]

            # Stream the response from the model
            response = model.stream(messages)

            def stream():
                # Stream the model's response
                for chunk in response:
                    model_response = chunk.content
                    yield 'data: %s\n\n' % json.dumps({"text": model_response})

                # Append the model's response to the history
                history.append({"role": "model", "content": model_response})

            return stream(), {'Content-Type': 'text/event-stream'}

        except Exception as e:
            return jsonify({"error": str(e)})

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
