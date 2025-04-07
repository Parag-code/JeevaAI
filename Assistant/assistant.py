import requests
import json
import platform
import os
import subprocess
import smtplib
from email.mime.text import MIMEText
import speech_recognition as sr
import pyttsx3

# Weather Assistant
def get_weather(city):
    try:
        # Using wttr.in service which doesn't require an API key
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            current_condition = data["current_condition"][0]
            weather_data = {
                "temperature": current_condition["temp_C"],
                "condition": current_condition["weatherDesc"][0]["value"],
                "humidity": current_condition["humidity"],
                "wind_speed": current_condition["windspeedKmph"],
                "pressure": current_condition["pressure"],
                "visibility": current_condition["visibility"],
                "feels_like": current_condition["FeelsLikeC"],
                "precipitation": current_condition["precipMM"],
                "cloud_cover": current_condition["cloudcover"]
            }
            return weather_data
        else:
            return f"Error: Could not fetch weather data for {city}"
    except Exception as e:
        return f"Weather service is unavailable. Error: {str(e)}"

# App Launcher Assistant
def open_app(app_name):
    try:
        if platform.system() == "Windows":
            os.system(f"start {app_name}")
        elif platform.system() == "Darwin":
            subprocess.call(["open", "-a", app_name])
        else:
            subprocess.call([app_name])
        return f"{app_name} launched successfully!"
    except Exception as e:
        return str(e)

# Email Assistant
def send_email(to, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv("EMAIL_USER")
        msg['To'] = to

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            server.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# Voice Assistant
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        return query
    except:
        return "Sorry, I could not understand." 