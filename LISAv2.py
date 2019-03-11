#! /usr/bin/env python
# -*-coding:utf-8-*-
# coding: utf8
import os
import speech_recognition as sr
from xml.dom import minidom
import sys
import random
import sqlite3
import RPi.GPIO as GPIO
import dht11
import requests
import json


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
instance = dht11.DHT11(pin = 14)
r = sr.Recognizer()
ya_uuid = '40fec3db0a61410083ad4c0485abdf42'
ya_api_key = '57724d1e-c970-4e12-bfd2-63cb8154d90c'
phrases_done = ["Готово", "Сделано", "Слушаюсь", "Есть", "Что-то еще?"]
phrases_listning = ["Я тут", "Слушаю", "Говори"]

 #os.system('echo "Ассист+ент зап+ущен" |festival --tts --language russian')


def convert_ya_asr_to_key():
    print(7)
    xmldoc = minidom.parse('./asr_answer.xml')
    print(7.5)
    itemlist = xmldoc.getElementsByTagName('variant')
    print(8)
    if len(itemlist) > 0:
        return itemlist[0].firstChild.nodeValue
    else:
        return False


def lisa_on():
    with sr.WavFile("send1.wav") as source:
        audio = r.record(source)
        print(1)
    try:
        t = r.recognize_sphinx(audio)
        print(1.5)
        print(t)
    except LookupError:
        print("Could not understand audio")

    return t == ("lisa")


def lisa_say(phrase):
    os.system(
        'curl "https://tts.voicetech.yandex.net/generate?format=wav&lang=ru-RU&speaker=alyss&emotion=good&key='+ya_api_key+'" -G --data-urlencode "text=' + phrase + '" > lisa_speech.wav')
    os.system('aplay lisa_speech.wav')


def lisa_say_good():
    randitem = random.choice(phrases_done)
    lisa_say(randitem)

def humidity():
    result = instance.read()
    return("температура "+ str(result.temperature) +" градусов по цельсию. влажность "+ str(result.humidity)+ " процентов")


try:
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    #c.execute("""CREATE TABLE ailogs()""")
    while True:
        os.system('arecord -f dat -r 16000 -d 3 -D plughw:1,0 send.wav')
        if lisa_on():
            print(2)
            randitem = random.choice(phrases_listning)
            lisa_say(randitem)
            os.system('arecord -f dat -r 16000 -d 3 -D plughw:1,0 send.wav')
            print(4)
            os.system(
                'curl -X POST -H "Content-Type: audio/x-wav" --data-binary "@send.wav" "https://asr.yandex.net/asr_xml?uuid='+ya_uuid+'&key='+ya_api_key+'&topic=queries" > asr_answer.xml')
            print(5)
            command_key = convert_ya_asr_to_key()
            print(6)
            if (command_key):
                os.system("rm send.wav")
                if (command_key in ['свет']):
                    os.system('')
                    lisa_say_good()
                    continue
                if (command_key in ['температура', 'влажность', 'комнатные условия']):
                    lisa_say(humidity())
                    continue
                if (command_key in ['вики', 'википедия', 'хочу узнать']):
                    lisa_say("Что вас интересует?")
                    os.system('curl -X POST -H "Content-Type: audio/x-wav" --data-binary "@send2.wav" "https://asr.yandex.net/asr_xml?uuid='+ya_uuid+'&key='+ya_api_key+'&topic=queries" > asr_answer.xml')
                    command_key = convert_ya_asr_to_key()
                    os.system('arecord -f dat -r 16000 -d 3 -D plughw:1,0 send.wav')
                    wiki_req = requests.get('https://ru.wikipedia.org/w/api.php?action=opensearch&search=python&format=json&utf8=true')
                    wiki_req_json = wiki_req.json()
                    print(wiki_req_json[2][0])
                    lisa_say(wiki_req_json[2][0])
                    continue
            else:
                lisa_say("команда не распознана, повтори")
        
        
except Exception:
    pass
lisa_say("Что-то пошло не так")