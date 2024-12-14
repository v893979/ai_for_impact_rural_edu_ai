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
import psycopg2
import certifi
from google.cloud import storage
from googleapiclient.discovery import build
from google.oauth2 import service_account

from html.parser import HTMLParser     # Import HTMLParser

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from xhtml2pdf import pisa
from io import BytesIO

from pdf2docx import Converter

import google.generativeai as genai
from google.generativeai import caching
import datetime
import time

app = Flask(__name__)  # Create the Flask app first
CORS(app, resources={r"/*": {"origins": "https://eduzone.pro"}})  # Then initialize CORS

#genai.configure(api_key=os.environ['API_KEY'])
genai.configure(api_key='AIzaSyAwUcBNlujGUVh0vRGSWPbZD1jnJkAtUJI')

@app.route("/generate_lesson", methods=["POST", "OPTIONS"])  # Add OPTIONS
@cross_origin(origin='https://eduzone.pro', headers=['Content-Type', 'Authorization'])
def generate_toc():
    if request.method == 'OPTIONS':  # Respond to preflight requests
        response = make_response(response)
        response.headers.add("Access-Control-Allow-Origin", "https://eduzone.pro")
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return ('', 204, response.headers)
    
    # Fetch the calling domain
    calling_domain = request.headers.get('Origin')
    if (calling_domain != "https://eduzone.pro"):
        return ('', 401, response.headers)
    
    data = request.get_json()    
    
    # conn = connect_to_db()
    # insert_data(conn, "postgres.book.tableofcontents", data)
    # conn.close()
    
    inputText = data.get("inputText")

    response = generateLesson(inputText)
    response = jsonify({"tableOfContents": response})
    response = make_response(response)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# Your Google Cloud Project ID
project_id = "kaggle-gemini-ai"

# Your GCS bucket name
bucket_name = "book-builder-pro"

# Path to your service account key file
service_account_key_file = "kaggle-gemini-ai-94286ec66fd4.json"

vertexai.init(project="kaggle-gemini-ai", location="us-central1")
# model = GenerativeModel(
# "gemini-flash-experimental",
# )
model = GenerativeModel(
"gemini-1.5-flash-002",
#"gemini-1.5-flash-8b",
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
    #chapterCount = 1
    
    #context = """Teach me a lesson on quadratic equations. Assume I know absolutely nothing about it."""

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
    
    htmlFormat1 = """<h2>Heading of the lesson</h2>

                    <ol>
                    <li><h3>Chapter 1: The Accused</h3>
                    <p>Introduce Daniel Hayes, a successful businessman accused of murdering his wife. He proclaims his innocence and hires Alex Ramsey, a rising star in the legal world.</p></li>

                    <li><h3>Chapter 2: First Impressions</h3>
                    <p>Alex meets Daniel in jail, sensing something amiss despite his confident demeanor.  She begins her initial investigation.</p></li>

                    <li><h3>Chapter 3: The Partner</h3>
                    <p>Alex discusses the case with her senior partner, Richard Nolan, a seasoned lawyer with a sharp mind and questionable ethics.  He advises caution.</p></li>

                    <li><h3>Chapter 4: The Victim</h3>
                    <p>Details of the murder emerge - seemingly a crime of passion, yet some evidence doesn't quite fit.</p></li>

                    <li><h3>Chapter 5: The Alibi</h3>
                    <p>Daniel's alibi is shaky, relying on the testimony of a known gambler with a history of deceit.</p></li>

                    <li><h3>Chapter 6: The Prosecution</h3>
                    <p>Meet the formidable prosecutor,  Eleanor Vance, known for her ruthless ambition and high conviction rate.</p></li>

                    <li><h3>Chapter 7: The Witness</h3>
                    <p>A mysterious woman contacts Alex, claiming to have vital information about the night of the murder.</p></li>

                    <li><h3>Chapter 8: Dead End</h3>
                    <p>The witness disappears before Alex can meet her, leaving a threatening message.</p></li>

                    <li><h3>Chapter 9: The Affair</h3>
                    <p>Alex uncovers evidence of Daniel's extramarital affair, casting doubt on his character.</p></li>

                    <li><h3>Chapter 10: Hidden Motives</h3>
                    <p>The mistress reveals she was pregnant with Daniel's child, adding a new layer of complexity to the case.</p></li>

                    <li><h3>Chapter 11: Financial Troubles</h3>
                    <p>Alex discovers Daniel's company was on the verge of bankruptcy, suggesting a financial motive for the murder.</p></li>

                    <li><h3>Chapter 12: The Break-In</h3>
                    <p>Alex's apartment is ransacked, and the files related to Daniel's case are stolen.</p></li>

                    <li><h3>Chapter 13: Threats</h3>
                    <p>Alex receives anonymous threats, warning her to drop the case.</p></li>

                    <li><h3>Chapter 14: The Judge</h3>
                    <p>The case is assigned to Judge Thompson, a notoriously tough judge with a reputation for favoring the prosecution.</p></li>

                    <li><h3>Chapter 15: Pre-Trial Motions</h3>
                    <p>Alex faces Vance in court, battling over evidence admissibility and witness credibility.</p></li>

                    <li><h3>Chapter 16: Jury Selection</h3>
                    <p>Both sides carefully select jurors, trying to gain an advantage.</p></li>

                    <li><h3>Chapter 17: Opening Statements</h3>
                    <p>Vance paints a picture of a cold-blooded killer, while Alex emphasizes reasonable doubt and the lack of concrete evidence.</p></li>

                    <li><h3>Chapter 18: The Maid's Testimony</h3>
                    <p>The housekeeper testifies to seeing Daniel arguing with his wife on the night of the murder.</p></li>

                    <li><h3>Chapter 19: Cross-Examination</h3>
                    <p>Alex skillfully undermines the maid's testimony, highlighting inconsistencies in her account.</p></li>

                    <li><h3>Chapter 20: Forensic Evidence</h3>
                    <p>The forensic expert presents DNA evidence linking Daniel to the crime scene.</p></li>

                    <li><h3>Chapter 21: The Expert Witness</h3>
                    <p>Alex brings in her own expert to challenge the validity of the DNA evidence.</p></li>

                    <li><h3>Chapter 22: The Gambler's Testimony</h3>
                    <p>The gambler takes the stand, providing a hesitant and unconvincing alibi for Daniel.</p></li>

                    <li><h3>Chapter 23: Impeachment</h3>
                    <p>Vance discredits the gambler by revealing his criminal record and gambling debts.</p></li>

                    <li><h3>Chapter 24: The Mistress's Testimony</h3>
                    <p>The mistress testifies about Daniel's desperation and anger in the weeks leading up to the murder.</p></li>

                    <li><h3>Chapter 25: Character Assassination</h3>
                    <p>Vance portrays Daniel as a manipulative and deceitful man capable of anything.</p></li>

                    <li><h3>Chapter 26: The Turning Point</h3>
                    <p>Alex uncovers a connection between Judge Thompson and Daniel's business rival.</p></li>

                    <li><h3>Chapter 27: Judicial Bias</h3>
                    <p>Alex suspects the judge is biased against Daniel and may be influencing the jury.</p></li>

                    <li><h3>Chapter 28: The Rival</h3>
                    <p>Alex investigates Daniel's rival, discovering he had both the motive and the opportunity to frame Daniel.</p></li>

                    <li><h3>Chapter 29: The Conspiracy</h3>
                    <p>Alex uncovers a complex web of corruption involving the rival, the judge, and a powerful political figure.</p></li>

                    <li><h3>Chapter 30: The Blackmail</h3>
                    <p>Alex realizes the judge is being blackmailed to ensure Daniel's conviction.</p></li>

                    <li><h3>Chapter 31: The Secret Meeting</h3>
                    <p>Alex secretly records a meeting between the judge and the rival, capturing their incriminating conversation.</p></li>

                    <li><h3>Chapter 32: The Confrontation</h3>
                    <p>Alex confronts the judge with the recording, threatening to expose his corruption.</p></li>

                    <li><h3>Chapter 33: The Deal</h3>
                    <p>The judge, fearing exposure, agrees to ensure a fair trial in exchange for Alex's silence.</p></li>

                    <li><h3>Chapter 34: New Evidence</h3>
                    <p>Alex presents new evidence pointing to the rival's involvement in the murder.</p></li>

                    <li><h3>Chapter 35: The Rival's Testimony</h3>
                    <p>The rival takes the stand, denying any wrongdoing but becoming increasingly nervous under Alex's cross-examination.</p></li>

                    <li><h3>Chapter 36: The Surprise Witness</h3>
                    <p>Alex calls a surprise witness who places the rival at the crime scene on the night of the murder.</p></li>

                    <li><h3>Chapter 37: Closing Arguments</h3>
                    <p>Vance makes a passionate plea for justice, while Alex emphasizes the evidence pointing to the real killer.</p></li>

                    <li><h3>Chapter 38: Jury Deliberations</h3>
                    <p>The jury struggles to reach a verdict, weighing the conflicting evidence and testimonies.</p></li>

                    <li><h3>Chapter 40: The Verdict</h3>
                    <p>The jury finds Daniel not guilty, much to Vance's dismay.</p></li>

                    <li><h3>Chapter 41: Aftermath</h3>
                    <p>Daniel is released from jail, grateful to Alex for her unwavering belief in his innocence.</p></li>
                    </ol>"""
    
    #if (bookLength=="XXL"):
    #detailsOfContext = "Please generate lesson in the format as shown in the following example " + htmlFormat1 + ". Please do not mention html tag or ` character. The context of the lesson is as followed: "+inputText
    #print(detailsOfTOC)

    # Try-catch block with retry logic
    for attempt in range(3):
        try:
            lessonContent = generate(inputText, generation_config, safety_settings)
            # If successful, break out of the loop
            break
        except Exception as e:
            print(f"Error generating table of contents (attempt {attempt + 1}): {e}")
            # Wait for a short time before retrying
            time.sleep(5)
            detailsOfContext = "Please generate moderated content as there was a content severity error in the previous attempt. " + detailsOfContext

            # If all attempts failed, handle the error appropriately
            if attempt == 2:
                print("Failed to generate table of contents after 3 attempts.")
                # You can raise an exception, return an error message, or handle the error in another way
                return "Error generating table of contents"
    
    

    return lessonContent

if __name__ == "__main__":
    #port = int(os.environ.get("PORT", 8080))  # Use 9091 as default
    app.run(host="0.0.0.0", port=8080)
    