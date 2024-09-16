import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
from datetime import datetime
from playsound import playsound

# Configuração do Gemini com modelo ajustado
def configurar_gemini():
    genai.configure(api_key="AIzaSyAxzvz-m_j4KA7vYpD756onCwGPKcwWal4")
    return genai.GenerativeModel('tunedModels/orderai-model-ub44uh16v2i3')

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


# Função para gerar resposta com Gemini usando o modelo ajustado
def gerar_resposta(texto):
    chat = model.start_chat(history=[])
    response = chat.send_message(texto)
    resposta = response.text[:1000]

    # Remover asteriscos e outros caracteres não desejados
    resposta_limpa = resposta.replace('*', '').replace('_', '')

    return resposta_limpa


# Função para informar as horas
def informar_horas():
    agora = datetime.now()
    hora = agora.hour
    minuto = agora.minute
    falar(f"Agora são {hora} horas e {minuto} minutos")


# Função principal
def main():
    ativo = False  # Variável para controle do estado
    while True:
        if not ativo:
            command = escutar()
            if "ok fiapinho" in command:
                ativo = True
                falar("Olá. Como posso te ajudar?")

        if ativo:
            command = escutar()
            if "que horas são" in command:
                informar_horas()
            elif "sair" in command:
                falar("Até mais!")
                ativo = False
            else:
                resposta_gemini = gerar_resposta(command)
                falar(resposta_gemini)


if __name__ == "__main__":
    main()
