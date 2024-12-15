# Gemini Flash 1.5 API & Vertex AI Conversation Agent

## Gemini Flash 1.5 API
In this project we have created a Gemini Flash 1.5 API using Python Flask.
This API is deployed on Cloud Run using Cloud Build. 
API can be accessed via API endpoint https://eduzone-original-ai-186050075223.us-central1.run.app/generate_lesson

### Example requests
``` {
    "inputText": "Teach me a lesson on quadratic equations. Assume I know absolutely nothing about it"
} 

{
    "inputText": "Generate a quiz on Algebra for grade 7 students. Generate 10 multiple choice questions"
} 
```

## Conversational agent using Agent builder
File with name exported_playbook_Default Generative Playbook.json is the exported agent builder code
This agent builder is integrated to [RuralEducation Website](https://kaggle-gemini-ai.ts.r.appspot.com/) 
You can access this agent by clicking on the conversational message at bottom right corner of the screen
This agent is trained on Australian Victorian Grade 7 Mathematics curriculam
You can ask queries to it such as "Explain chapter 1 to me"
