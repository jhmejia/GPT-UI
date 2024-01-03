from flask import Flask, request, render_template, session, jsonify
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Used to keep the session secure

# Initialize the OpenAI client

GPT_MODEL = "gpt-4-1106-preview"  # Default model
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def init_session():
    # Initialize session variables if they don't exist
    if 'history' not in session:
        session['history'] = []
    if 'role' not in session:
        session['role'] = "You are a helpful assistant."
    if 'temperature' not in session:
        session['temperature'] = 0.3

@app.route('/')
def index():
    init_session()
    return render_template('index.html', history=session['history'], role=session['role'], temperature=session['temperature'])

@app.route('/ask', methods=['POST'])
def ask():

    # Initialize session variables if they don't exist
    init_session()

    print(request.form)
    question = request.form['question']
    role = request.form['role']
    temperature = float(request.form['temperature'])
    session['role'] = role
    session['temperature'] = temperature

    # Here you would integrate with the GPT-4 API and get the response
    # For this example, I'll just echo the question
    # response = f"GPT-4 response to '{question}' with role '{role}' and temperature '{temperature}'"

    # Turn messages into a list by combining role, history, and question

    messages = []

    # First add the system role
    messages.append({"role": "system", "content": session['role']})
    # Then add the history
    messages.extend(session['history'])
    # Finally add the question
    messages.append({"role": "user", "content": question})


    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=temperature,
    )
    
    
    response_message = str(response.choices[0].message.content)

    # Save the conversation history in the session
    session['history'].append({"role": "user", "content": question})
    session['history'].append({"role": "assistant", "content": response_message})

    return jsonify(role=role, question=question, response=response_message)

@app.route('/clear', methods=['POST'])
def clear():
    session['history'] = []
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)