import threading
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import streamlit as st
import ollama  # Ensure you have the ollama package available
import requests

# Initialize FastAPI app
app = FastAPI()

# Define a request model for input validation
class SentenceInput(BaseModel):
    sentence: str

# Define the system behavior as a constant
SYSTEM_BEHAVIOR = """
You are a text evaluator. Your task is to label a sentence as 
'incomplete' only if it does not make sense, even after adjusting for missing 
spaces. If a sentence lacks proper spacing but can be meaningful when spaces 
are added, you should label it as 'complete'. Provide only one label: 
'incomplete' or 'complete', and one line explanation for your decision.
"""

# FastAPI route for evaluating the sentence
@app.post("/evaluate/")
async def evaluate_sentence(input: SentenceInput):
    user_sentence = input.sentence.strip()
    
    if user_sentence.lower() == "stop":
        return {"evaluation": "Exiting the program."}
    
    # Define the chat model with user input
    response = ollama.chat(model='llama3', messages=[
        {
            'role': 'system',
            'content': SYSTEM_BEHAVIOR
        },
        {
            'role': 'user',
            'content': user_sentence
        },
    ])
    
    return {"evaluation": response['message']['content']}

# Function to run the FastAPI server
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Start the FastAPI server in a separate thread
threading.Thread(target=run_fastapi, daemon=True).start()

# Set up the Streamlit app
st.title("Sentence Evaluator")

st.write("This will be used to check if complete sentences are used in the variable parts of message templates, which could be used for phishing.")

st.write("Enter a sentence to evaluate whether it is complete or incomplete.")

user_input = st.text_input("Your Sentence:")

if st.button("Evaluate"):
    if user_input:
        # Prepare the payload for the API request
        payload = {"sentence": user_input}
        
        # Send the POST request to the FastAPI endpoint
        response = requests.post("http://localhost:8000/evaluate/", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"Evaluation: {result['evaluation']}")
        else:
            st.error("Error evaluating the sentence.")
    else:
        st.warning("Please enter a sentence.")
