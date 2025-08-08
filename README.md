# Voice Chatbot
This project is a full stack voice enabled chatbot that integrates real time speech-to-text (STT), semantic search, large language model (LLM) responses, and text-to-speech (TTS) streaming. 
The backend is built with Flask and SocketIO, while the frontend uses React with WebSocket communication for realtime interaction. 
The system processes audio input, converts it to text, retrieves relevant context using Pinecone, generates responses with OpenAI's GPT model, and streams audio output using ElevenLabs.


A manual_data.json file with financial knowledge snippets (already provided)

## Features

Realtime Audio Processing: Converts audio input to text using Whisper (local GPU or remote Colab).


Semantic Search: Retrieves relevant financial context from a Pinecone vector database.


LLM Powered Responses: Generates answers using OpenAI's GPT-4o model.


Text-to-Speech Streaming: Converts responses to audio using ElevenLabs and streams them to the client.


WebSocket Communication: Enables realtime interaction between the frontend and backend.


Voice Activity Detection (VAD): Uses @ricky0123/vad-web (Silerio VAD) for detecting speech in the browser.


Financial Knowledge Base: Supports manual data input stored in manual_data.json for semantic search.


## Installation

### Backend


cd Backend

Create a virtual environment and activate it:
python -m venv venv
venv\Scripts\activate


Install dependencies:pip install -r requirements.txt


Set up environment variables in a .env file:


OPENAI_API_KEY=""


PINECONE_API_KEY=""


ELEVEN_LABS_API_KEY=""


NGROK_AUTH_TOKEN=""  # Optional for Colab (Remote STT to utilize free GPU)


Upload VoiceBotMicroServices.ipynb to your Colab environment.


In Colab's Secret set:


Name = ngrok


Value = your ngrok auth token


Provide notebook access to it


Run the Colab script to install dependencies.


Use the ngrok public URL provided in the Colab output and paste it stt_helper.py :  COLAB_BASE_URL


(Once everything is in same cloud infra with GPU, we can ignore colab and ngrok setup)


## Running the Application


Create Pinecone vector database:
python pinecone_config.py


If you want to put manual data yourself :


python manual_data_create.py


then


python manual_data_load.py  ( Also need to change the prompt for LLM ) 



Start the Flask server:


python app2.py



The server will run on http://localhost:5000.


### Frontend


cd Frontend


npm i


npm run dev


## Usage


### Audio Input: 


The frontend uses VAD to detect speech and sends audio blobs to the backend via WebSocket (audio_blob event).


Audio is saved temporarily in the Uploads folder and processed by the backend.


### Processing:


STT: Audio is converted to text using Whisper (local if GPU is available, otherwise via Colab).



Semantic Search: The text query retrieves relevant financial context from Pinecone.



LLM Response: OpenAI's GPT model generates a response based on the query and context.



TTS: The response is converted to audio using ElevenLabs and streamed back as audio chunks.


### Output:


The frontend receives partial text responses (bot_partial event) and audio chunks (bot_audio_chunk event).



The final response is sent via the bot_response event.



Audio chunks are played sequentially in the browser using the Audio API.

