#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, jsonify, make_response, app
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
from flask_cors import CORS, cross_origin
from google.oauth2 import service_account
import os
from google.auth.transport.requests import AuthorizedSession
from google.auth import default
from google.cloud import storage
from googleapiclient.discovery import build
from google.oauth2 import service_account

from html.parser import HTMLParser     # Import HTMLParser

import google.generativeai as genai
from google.generativeai import caching

app = Flask(__name__)  # Create the Flask app first
CORS(app, resources={r"/*": {"origins": "https://eduzone.pro"}})  # Then initialize CORS

genai.configure(api_key='YOUR_API_KEY')

@app.route("/generate_lesson", methods=["POST", "OPTIONS"])
@cross_origin(origin='https://eduzone.pro', headers=['Content-Type', 'Authorization'])
def generate_lesson():
    if request.method == 'OPTIONS':
        response = make_response()  # Create an empty response for OPTIONS
        response.headers.add("Access-Control-Allow-Origin", "https://eduzone.pro")
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return ('', 204, response.headers)

    calling_domain = request.headers.get('Origin')
    if calling_domain != "https://eduzone.pro": 
        return ('', 401) 

    data = request.get_json()    

    inputText = data.get("inputText")

    lessonContent = generateLesson(inputText)  # Call the function to generate the lesson
    response = jsonify({"tableOfContents": lessonContent})  # Create the JSON response here
    return response # Flask automatically handles the content-type header for jsonify responses.

# Your Google Cloud Project ID
project_id = "YOUR_PROJECT_ID"

# Path to your service account key file
service_account_key_file = "YOUR_SERVICE_ACCOUNT_KEY.json"

vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")

model = GenerativeModel(
"gemini-1.5-flash-002",
)
    
def generate(text1, generation_config, safety_settings):
  responses = model.generate_content(
      [text1],
      generation_config=generation_config,
      safety_settings=safety_settings,
      stream=True,
  )
  
  finalResponse = ''
  for response in responses:
    finalResponse = finalResponse + response.text
    
  return finalResponse

def generateLesson(inputText):
    temparature = 2

    context = """Please give the output in formatted HTML. Context is as follows:""" + inputText

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": temparature,
        "top_p": 0.95,
    }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
    
    # Try-catch block with retry logic
    for attempt in range(3):
        try:
            lessonContent = generate(context, generation_config, safety_settings)
            # If successful, break out of the loop
            break
        except Exception as e:
            print(f"Error generating lesson (attempt {attempt + 1}): {e}")

    return lessonContent

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    