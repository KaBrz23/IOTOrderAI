import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
from datetime import datetime
import random
import requests
from playsound import playsound

# Configuração do Gemini
def configurar_gemini():
    genai.configure(api_key="AIzaSyBELFZo47yf2d-1c39QJH7GXsu_ZjuAqIU")
    return genai.GenerativeModel('gemini-pro')

model = configurar_gemini()

recognizer = sr.Recognizer()

# Função de fala
def falar(text):
    tts = gTTS(text=text, lang='pt-br', slow=False)  # Ajuste a velocidade da voz
    filename = "voice.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

# Função para ouvir comando de voz
def escutar():
    with sr.Microphone() as source:
        print("Escutando...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, language='pt')
            print(f"Você disse: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Desculpe, não entendi o que você disse.")
            return ""
        except sr.RequestError:
            print("Erro ao conectar com o serviço de reconhecimento de voz.")
            return ""

# Função para gerar resposta com Gemini
def gerar_resposta(texto):
    chat = model.start_chat(history=[])
    response = chat.send_message(texto)
    return response.text[:150]

# Função para informar as horas
def informar_horas():
    agora = datetime.now()
    hora = agora.hour
    minuto = agora.minute
    falar(f"Agora são {hora} horas e {minuto} minutos")

# Função principal
def main():
    while True:
        command = escutar()
        if "ok fiapinho" in command:
            falar("Olá. Como posso te ajudar?")
            command = escutar()

            if "que horas são" in command:
                informar_horas()
            else:
                resposta_gemini = gerar_resposta(command)
                falar(resposta_gemini)

if __name__ == "__main__":
    main()