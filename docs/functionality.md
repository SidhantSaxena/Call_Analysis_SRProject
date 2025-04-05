# __Functionality and Usage__

## __Application Features__
- __Frontend__: Reads a transcript(.txt) and audio(.wav) file input file and generates analysis for it. Incase audio file is provided, it uses async POST/GET functions to fetch the transcript from the AI model via FAST APIs. Based on dynamic user interaction, the UI provides interactive charts details on the sentiment analysis of the call and the Guideline Compliance.
- __Rule Based Sentiment Analysis/Guidance Compliance__: A predefined set of hardcoded rules, stored in a YAML file for easy modification. Used RapidFuzz’s token_sort_ratio (threshold: 55) to compare input text against predefined phrases (Greetings, Disclaimers, Closing Statements) and return matched categories with counts. For compliance, regex is used to detect and flag sensitive data like account details and passwords.
- __Backend__: FastAPI enables asynchronous audio uploads and transcription retrieval. The frontend POSTs a .wav file, which the backend saves locally and returns its path. A GET request processes the audio with Whisper, saves the transcript, and updates the session state. Since transcription time varies by file size, an HTTP timeout of 1000s is set. Multithreading ensures a non-blocking event loop for concurrent requests, while logging tracks API activity for debugging and monitoring.

## __Pre Requisites__
- Linux OS(>= 22.04)
- Python(=3.12) 
- just (use ```sudo apt install just``` incase not installed)

## __Running the Application__
1. Clone the repository:
```git clone https://github.com/ashish142402004/Call_Analysis_SRProject.git```
2. Inside the main directory run the following commands:
    - For initial setup ```just setup```
    - To start the frontend and backend use ```just run```
    - The frontend runs on ```http://localhost:8501```
    - __Note:__ Please check if the backend is running before testing. Wait for a message like ```Server started at http://0.0.0.0:8000```


<div class="grid cards" markdown>
  - [__<- App Architecture__](architecture.md)
  - [__Learning Experience ->__](experience.md)
</div>