import speech_recognition as sr
import time
import pyttsx3 as pyttsx
import threading


def listen():
    def say(text):
        engine = pyttsx.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 0.3)
        engine.say(text)
        engine.runAndWait()

    r = sr.Recognizer()
    m = sr.Microphone()
    m.RATE = 44100
    m.CHUNK = 512

    say("How can I help you?")
    print("A moment of silence, please...")
    with m as source:
        r.adjust_for_ambient_noise(source)
        if (r.energy_threshold < 2000):
            r.energy_threshold = 2000
        print("Set minimum energy threshold to {}".format(r.energy_threshold))
        print("Say something!")
        audio = r.listen(source)
        print("Got it! Now to recognize it...")
        say("one moment, let me think")
        try:
            speechtext = r.recognize(audio)
            print("You said: " + speechtext)
        except LookupError:
            print("sorry, I didn't catch that")
            say("sorry, I didn't catch that")


while True:
    listen()