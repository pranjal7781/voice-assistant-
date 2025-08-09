"""
Nexa - Voice Assistant (
"""

import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import platform
import subprocess
import sys
from pathlib import Path


# Text-to-Speech Engine
def init_engine(preferred_voice: str | None = None):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    if preferred_voice:
        preferred_voice = preferred_voice.lower()
        for v in voices:
            name = (v.name or "").lower()
            if preferred_voice in name or preferred_voice in (v.id or "").lower():
                engine.setProperty("voice", v.id)
                break
        else:
            try:
                engine.setProperty("voice", voices[1].id)
            except IndexError:
                engine.setProperty("voice", voices[0].id)
    else:
        try:
            engine.setProperty("voice", voices[1].id)
        except Exception:
            engine.setProperty("voice", voices[0].id)

    engine.setProperty("rate", 170)
    return engine

engine = init_engine(preferred_voice=None)

def speak(text: str, block: bool = True):
    engine.say(text)
    if block:
        engine.runAndWait()




def wish_user():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("Hello, I am Nexa. How can I help you today?")

def safe_open_path(path_str: str):
    path = Path(path_str).expanduser()
    if not path.exists():
        speak(f"I couldn't find {path_str}")
        return False

    try:
        if platform.system() == "Windows":
            os.startfile(str(path))
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        speak(f"Opening {path.name}")
        return True
    except Exception:
        speak("Sorry, I couldn't open that.")
        return False


# Listening / Recognition

recognizer = sr.Recognizer()

def listen_command(timeout: float = 5, phrase_time_limit: float = 6) -> str:
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
        except Exception:
            pass

        speak("Listening...", block=False)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("No speech detected (timeout).")
            return fallback_text_input()

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-US")
        print(f"User said: {query}")
        return query
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        speak("Sorry, I did not understand. Please type your command or try again.")
        return fallback_text_input()
    except sr.RequestError:
        speak("Speech recognition service is unavailable. Please type your command.")
        return fallback_text_input()
    except Exception:
        return fallback_text_input()

def fallback_text_input() -> str:
    try:
        text = input("Type command (or press Enter to skip): ").strip()
        return text
    except KeyboardInterrupt:
        return "exit"


# Command Processing

def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {now}")
    print("Time:", now)

def tell_date():
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
    speak(f"Today is {today}")
    print("Date:", today)

def search_wikipedia(query: str):
    try:
        speak("Searching Wikipedia...")
        summary = wikipedia.summary(query, sentences=2, auto_suggest=False, redirect=True)
        print("Wikipedia:", summary)
        speak("According to Wikipedia, " + summary)
    except wikipedia.DisambiguationError as e:
        options = e.options[:5]
        speak("Your query is ambiguous. Did you mean: " + ", ".join(options) + "?")
    except Exception:
        speak("I couldn't fetch results from Wikipedia.")

def open_website(url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        webbrowser.open(url)
        speak(f"Opening {url}")
    except Exception:
        speak("I couldn't open the website.")

def process_command(raw: str) -> bool:
    if not raw:
        return True

    query = raw.lower()

    if "hello" in query or "hi" in query:
        speak("Hello! How can I assist you?")
    elif "time" in query and "date" not in query:
        tell_time()
    elif "date" in query:
        tell_date()
    elif "wikipedia" in query:
        query = query.replace("wikipedia", "").strip()
        if not query:
            speak("What should I search on Wikipedia?")
            q2 = listen_command()
            if q2:
                search_wikipedia(q2)
        else:
            search_wikipedia(query)
    elif "open youtube" in query:
        open_website("https://youtube.com")
    elif "open google" in query:
        open_website("https://google.com")
    elif "open browser" in query or "open web" in query:
        open_website("https://google.com")
    elif query.startswith("open ") and len(query.split()) == 2:
        site = query.split()[1]
        open_website(f"{site}.com")
    elif "play music" in query:
        music_folder = Path.home() / "Music"
        if not music_folder.exists():
            speak("I couldn't find the Music folder. Please type the full path to your music folder.")
            path = fallback_text_input()
            if path:
                safe_open_path(path)
        else:
            safe_open_path(str(music_folder))
    elif "open" in query and ("file" in query or "application" in query):
        speak("Please type the path to the file or application you want to open.")
        path = fallback_text_input()
        if path:
            safe_open_path(path)
    elif "exit" in query or "stop" in query or "quit" in query:
        speak("Are you sure you want to exit? Say yes to confirm.")
        confirm = listen_command().lower()
        if "yes" in confirm or confirm.startswith("y"):
            speak("Goodbye. Have a nice day!")
            return False
        else:
            speak("Continuing...")
            return True
    elif "help" in query:
        speak("You can say: time, date, wikipedia, open YouTube, open Google, play music, or exit.")
    else:
        speak("I didn't find a direct command. Should I search the web for that?")
        confirm = listen_command().lower()
        if "yes" in confirm or confirm.startswith("y"):
            open_website(f"https://www.google.com/search?q={raw.replace(' ', '+')}")
        else:
            speak("Okay. Let me know what else I can do.")
    return True


# Main

def main():
    speak("Starting Nexa.")
    wish_user()
    running = True
    try:
        while running:
            cmd = listen_command()
            if not cmd:
                continue
            running = process_command(cmd)
    except KeyboardInterrupt:
        speak("Interrupted. Exiting. Goodbye!")
    except Exception:
        speak("A fatal error occurred. Closing now.")
    finally:
        try:
            engine.stop()
        except Exception:
            pass

if __name__ == "__main__":
    main()

