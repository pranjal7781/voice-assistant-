import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os

engine = pyttsx3.init()
print(engine.getProperty('voices'))
voices = engine.getProperty("voices")
engine.setProperty('voice', voices[1].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

    
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")
        
    elif hour>=12 and hour<18:
        speak("Good Afternoon!")
        
    else:
        speak("good Evening!")
    speak("hello sir,i am nexa, how can i help you")
def refferal():
    # its take microphone input from the user and returns string output
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listining...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-us')
        print(f"user said: {query}\n")
        
    except Exception as e:
        print("Say that again please..")
        return "None"
    return query
        
        
if __name__ == "__main__":
     wishMe()
     while 1:
         query = refferal().lower()
         
         if "hello" in query:
             print("Hello sir ! How are you?, how can i help you...")
             speak("Hello sir ! How are you?, how can i help you...")

         elif 'wikipedia' in query:
             speak('Searching Wikipedia....')
             query = query.replace("wikipedia", "")
             results = wikipedia.summary(query, sentences=2)
             speak("according to wikipedia")
             print(results)
             speak(results)
             
         elif 'open youtube' in query:
             webbrowser.open("youtube.com")
             
         elif 'open google' in query:
            webbrowser.open("google.com")

         elif "exit" in query or "stop" in query:
            speak("goodbye sir, see you later, have a nice day")
            break