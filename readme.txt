python3 -m venv venv 
venv\Scripts\activate

pip install Flask
pip install --upgrade google-cloud-aiplatform
pip install vertexai
gcloud auth application-default login

python app.py
http://127.0.0.1:5000/hello