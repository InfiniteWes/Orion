from openai import OpenAI
import time
from pathlib import Path
from pygame import mixer  # Load the popular external library
import time
import os
import requests

tts_enabled = True

# Initialize the client
client = OpenAI()
mixer.init()
# Retrieve the assistant
assistant = client.beta.assistants.retrieve("Insert_your_assistant_ID_here")
#create empty thread
jarvis_thread = "Insert_your_thread_id_here"
thread = client.beta.threads.retrieve(jarvis_thread)

# Function to ask a question to the assistant
def ask_question_standard(question):
    #this is an example of how you can feed in context
    #Hint LLMs won't know the time or date unless you tell them
    date_and_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    context = """
    You are an assistant named Jarvis like from the ironman movies. 
    You are to act like him and provide help as best you can.  
    Be funny and witty. Keep it brief and serious. 
    Be a little sassy in your responses. 
    You have a variety of smart devices to control. 
    You can control them by ending your sentence with #light1-off like this. 
    Only use commands like this if I tell you to do so. nd your sentence with #lamp-1 for on and #lamp-0 for off. 
    Response in less than 80 words. 
    """ + date_and_time
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[
        {"role": "system", "content": context},
        {"role": "user", "content": question}
        
    ]
    )
    return response.choices[0].message.content

# Try this if you want Jarvis to remember the conversation
def ask_question_memory(question):
    global thread
    global thread_message
    thread_message = client.beta.threads.messages.create(
        thread.id,
        role="user",
        content=question,
        )
    # Create a run for the thread
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
    )
    # Wait for the run to complete
    while True:
        run_status = client.beta.threads.runs.retrieve(
          thread_id=thread.id,
          run_id=run.id
        )
        if run_status.status == 'completed':
            break
        elif run_status.status == 'failed':
            return "The run failed."
        time.sleep(1)  # Wait for 1 second before checking again
    # Retrieve messages after the run has succeeded
    messages = client.beta.threads.messages.list(
      thread_id=thread.id
    )
    return messages.data[0].content[0].text.value

# Function to generate TTS and return the file path using ElevenLabs
def generate_tts(sentence, speech_file_path, model_id="eleven_multilingual_v2"):
    # change the query string desired value from 0 to 4 for latency optimization.
    querystring={"optimize_streaming_latency":"<desired value>"}

    """
    Within the URL change the voice_id to your desired voice id key which
    can be found at https://elevenlabs.io/app/voice-lab
    """
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    payload = {
        "text": sentence,
        "model_id": model_id,
        "voice_settings": {
            "stability": 1, # Changes the voices stability or variety of speech.
            "similarity_boost": 0.5, # Changes the similarity of the voice.
            "style": 0.5, # Adds style to the voice, based off the original audio.
            "use_speaker_boost": True
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer <Your-API-Key>"  # Use your actual API key here
    }
    
    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    if response.status_code == 200:
        with open(speech_file_path, 'wb') as f:
            f.write(response.content)
        return str(speech_file_path)
    else:
        return None

# Function to perform Text-to-Speech and play it using mixer
def TTS(text):
    speech_file_path = Path("speech.mp3")
    file_path = generate_tts(text, speech_file_path)
    if file_path:
        play_sound(file_path)
        while mixer.music.get_busy():  # Wait for the mixer to finish
            time.sleep(1)
        mixer.music.unload()
        os.remove(file_path)  # Delete the file after playing
        return "done"
    else:
        return "Error in generating speech"

# Function to play a sound file
def play_sound(file_path):
    mixer.music.load(file_path)
    mixer.music.play()