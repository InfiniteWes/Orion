#This is an example for a later tutorial of how I trigger actions based on the response from Jarvis
#This simply prints things out if he says any of these commands
#I use this method for triggering 3d prints, laser cutting, and other things

import requests

def get_instagram_profile():
    url = "https://instagram-scraper-2022.p.rapidapi.com/ig/info_username/"

    querystring = {"username": "<YOUR_USERNAME>"}

    headers = {
        "X-RapidAPI-Key": "<YOUR_API_KEY>",
        "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()['user']
        return {
            'username': data.get('username', ''),
            'followers': data.get('follower_count', ''),
            'following': data.get('following_count', ''),
        }
    else:
        return None

def get_weather_forecast():
    url = "https://weatherbit-v1-mashape.p.rapidapi.com/forecast/3hourly"

    querystring = {"lat": "<YOUR_LATITUDE>", "lon": "<YOUR_LONGITUDE>", "units": "<UNIT_OF_CHOICE>", "lang": "<LANGUAGE>"}
    
    headers = {
        "X-RapidAPI-Key": "<YOUR_API_KEY>",
        "X-RapidAPI-Host": "weatherbit-v1-mashape.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()['data']
        current_weather = data[0]
        return {
            'temp': current_weather['temp'],
            'description': current_weather['weather']['description']
        }
    else:
        return None


def parse_command(input_text):
    input_text = input_text.lower()

    if "print" in input_text:
        return "Hello World!"
    elif "what's the weather" in input_text or "weather" in input_text:
        weather_info = get_weather_forecast()
        if weather_info:
            return f"It's currently {weather_info['temp']} degrees and {weather_info['description']}."
        else:
            return "Sorry, I couldn't get the weather information."
    elif "instagram status" in input_text or "instagram" in input_text:
        profile = get_instagram_profile()
        if profile:
            return f"{profile['username']} has {profile['followers']} followers and {profile['following']} following."
        else:
            return "Sorry, I couldn't get the Instagram profile information."
    elif "light on" in input_text:
        return "Light is on!"
    elif "light off" in input_text:
        return "Light is off!"
    elif "exit" in input_text:
        print("Exiting...")
        exit()
    return ""