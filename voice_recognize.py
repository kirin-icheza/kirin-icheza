import speech_recognition as sr
import time
import threading

def listen():
    
    r = sr.Recognizer() #Create a new Recognizer instance
    m = sr.Microphone() #Create a new Microphone instance
    m.RATE = 44100
    m.CHUNK = 512
   
    print("A moment of silence, please...")
    with m as source:
        r.adjust_for_ambient_noise(source)
        if(r.energy_threshold < 2000): #threshold - 최소 들을 수 있는 소리 크기, threshold보다 낮으면 인지 못함
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
                print("You said: " + speechtext)
        except LookupError:
            print("sorry, I didn't catch that")

while True:
    listen()