import pyttsx3
import speech_recognition as sr
import os
from fuzzywuzzy import fuzz
import datetime
import win32com.client as wincl

opts = {
    "alias": ("pythonguru", "пайтонгуру", "гурупайтон", "квант"),
    "tbr": (
        "скажи",
        "расскажи",
        "покажи",
        "сколько",
        "произнеси",
        "как",
        "сколько",
        "поставь",
        "переведи",
        "засеки",
        "запусти",
        "сколько будет",
    ),
    "cmds": {
        "ctime": (
            "текущее время",
            "сейчас времени",
            "который час",
            "время",
            "какое сейчас время",
        ),
        "startStopwatch": ("запусти секундомер", "включи секундомер", "засеки время"),
        "stopStopwatch": ("останови секундомер", "выключи секундомер", "останови"),
        "stupid1": (
            "расскажи анекдот",
            "рассмеши меня",
            "ты знаешь анекдоты",
            "шутка",
            "прикол",
        ),
        "calc": (
            "прибавить",
            "умножить",
            "разделить",
            "степень",
            "вычесть",
            "поделить",
            "х",
            "+",
            "-",
            "/",
        ),
        "shutdown": (
            "выключи",
            "выключить",
            "отключение",
            "отключи",
            "выключи компьютер",
        ),
        "conv": ("валюта", "конвертер", "доллар", "руб", "евро"),
        "internet": ("открой", "вк", "гугл", "сайт", "вконтакте", "ютуб"),
        "translator": ("переводчик", "translate"),
        "deals": ("дела", "делишки", "как сам", "как дела"),
    },
}

startTime = 0
speak_engine = pyttsx3.init()
voices = speak_engine.getProperty("voices")
speak_engine.setProperty("voice", voices[2].id)
r = sr.Recognizer()
m = sr.Microphone(device_index=1)
voice = "str"


def execute_cmd(text):
    print(text)


def speak(what):
    print(what)
    speak = wincl.Dispatch("SAPI.SpVoice")
    speak.Speak(what)


def callback(recognizer, audio):
    try:
        global voice
        voice = recognizer.recognize_google(audio, language="ru-RU").lower()

        print("[log] Распознано: " + voice)

        if voice.startswith(opts["alias"]):
            cmd = voice

            for x in opts["alias"]:
                cmd = cmd.replace(x, "").strip()

            for x in opts["tbr"]:
                cmd = cmd.replace(x, "").strip()
            voice = cmd
            # распознаем и выполняем команду
            cmd = recognize_cmd(cmd)
            execute_cmd(cmd["cmd"])

    except sr.UnknownValueError:
        print("[log] Голос не распознан!")
    except sr.RequestError as e:
        print("[log] Неизвестная ошибка, проверьте интернет!")


def listen():
    with m as source:
        r.adjust_for_ambient_noise(source)
    stop_listening = r.listen_in_background(m, callback)
    while True:
        time.sleep(0.1)


def recognize_cmd(cmd):
    RC = {"cmd": "", "percent": 0}
    for c, v in opts["cmds"].items():
        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > RC["percent"]:
                RC["cmd"] = c
                RC["percent"] = vrt
    return RC


if __name__ == "__main__":
    import time
    import datetime

    now = datetime.datetime.now()

    if now.hour >= 6 and now.hour < 12:
        speak("Доброе утро!")
    elif now.hour >= 12 and now.hour < 18:
        speak("Добрый день!")
    elif now.hour >= 18 and now.hour < 23:
        speak("Добрый вечер!")
    else:
        speak("Доброй ночи!")

    listen()
