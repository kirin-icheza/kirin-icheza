import speech_recognition as sr
import time
import threading
import server

def listen():
    global light
    r = sr.Recognizer()
    m = sr.Microphone()
    m.RATE = 44100
    m.CHUNK = 512

    print("A moment of silence, please...")
    with m as source:
        r.adjust_for_ambient_noise(source)
        if (r.energy_threshold < 2000):
            r.energy_threshold = 2000
        print("Set minimum energy threshold to {}".format(r.energy_threshold))
        print("Say something!")
        audio = r.listen(source)
        print("Got it! Now to recognize it...")
        try:
            speechtext = r.recognize_google(audio,language = 'ko',show_all=True) #Load Google Speech Recognition API
            print(type(speechtext)) #dict
            if len(speechtext) == 0: #아무 말도 인식 안되었을 때
                pass
            else:
                speechtext = speechtext['alternative'][0]['transcript'] #신뢰도가 가장 높은 말
                speechtext = speechtext.replace(' ', '')
                print("You said: " + speechtext)
                if '불켜' in speechtext:
                    light = 1
                    print('말로 불을 켰음', light)
                if '불꺼' in speechtext:
                    light = 0
                    print('말로 불을 껐음', light)
                    
        except LookupError:
            print("sorry, I didn't catch that")

def main():
    while True:
        listen()
