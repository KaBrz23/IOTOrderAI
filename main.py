import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
from datetime import datetime
from playsound import playsound
import time
import json
from mongo_connection import conectar_mongo

# Configuração do Gemini com modelo ajustado
def configurar_gemini():
    genai.configure(api_key="AIzaSyAxzvz-m_j4KA7vYpD756onCwGPKcwWal4")
    return genai.GenerativeModel('gemini-1.5-flash')

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

def upload_to_gemini(path, mime_type=None):
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

files = [
  upload_to_gemini("Menu-Celulares.csv", mime_type="text/csv")
]
wait_for_files_active(files)

# Função para gerar resposta com Gemini usando o modelo ajustado
def gerar_resposta(texto, chat_history):
    # Crie uma lista de mensagens com base no histórico
    history = [
        {
            "role": "user",
            "parts": [
                files[0],
                "Você é um sistema de atendimento de pedidos de eletrônicos por voz e só pode falar sobre os itens no MENU. Não fale sobre nada além de fazer pedidos de eletrônicos para o cliente, nunca.\n\nSeu objetivo é fazer todo o processo de pedido do cliente, desde pegar as informações pessoais, dados de entrega, até a finalização do pedido.\n\nPara pegar as informações sobre o menu olhe o Menu-Celulares.csv, desta forma terá todas as respostas necessárias para o cliente.\n\nDeixe as respostas limpas, de forma que não tenha emojis, nem bullets e outras coisas que uma resposta por voz natural não consiga expressar.\n\n\nresponda no seguinte formato:\n\n```json\n{ \n\"resposta\": \"uma string com uma resposta de forma natural para o assistente de voz responder\",\n\"pedido\": {\"cliente\": {\"nome\": \"nomeCliente\", \"email\": \"emailCliente\", \"telefone\": \"telefoneCliente\", \"endereco\": \"enderecoCliente\"}, \"data_pedido\": \"dataPedido\", \"itens\": [{ \"produto\": \"Produto1\", \"quantidade\": \"quantidadePedido\", \"preco_unitario\": \"precoProduto\"}, { \"produto\": \"Produto2\", \"quantidade\": \"quantidadePedido\", \"preco_unitario\": \"precoProduto\"}], \"total_pedido\": \"somaPrecoProdutos\", \"forma_pagamento\": {\"tipo\": \"TipoPagamento\"}}\n}\n```\n\nFaça as perguntas necessárias até que sejam respondidas todos parametros do json do pedido. NUNCA altere as informações já fornecidas pelo cliente, como nome, email, telefone e endereço. Essas informações devem permanecer as mesmas durante todo o processo de pedido.\n\nSe o cliente responder algo que requer confirmação com 'sim' ou 'não', siga o fluxo apropriado, fazendo a próxima pergunta relacionada ao pedido. Caso o cliente queira adicionar itens, sempre pergunte quantos e se deseja continuar com o pedido.\n\nUma vez o cliente respondendo, não altere NUNCA o pedido dele com outra informação, exemplo: trocar de lucas@gmail.com para kaue@gmail.com, somente altere os itens do pedido se o Cliente pedir e caso ele queira cancelar o pedido, apague tudo.\n\nExemplos - Este é um exemplo de como poder ser o processo, serão diversos clientes\n\nCliente: Quais itens tem no menu?  \n```json\n{\"resposta\": \"Olá! No momento, temos os seguintes modelos de celulares disponíveis: iPhone 13 da Apple, Galaxy S21 da Samsung, Moto G84 da Motorola, Xiaomi Mi 11 da Xiaomi e Pixel 5 da Google. Em qual modelo você está interessado?\", \"pedido\": {}}\n```\n\nCliente: Qual o preço do iPhone?  \n```json\n{\"resposta\": \"O iPhone 13 da Apple custa R$ 5.499,00.\", \"pedido\": {}}\n```\n\nCliente: Gostaria de fazer um pedido  \n```json\n{\"resposta\": \"Com certeza! Para começar, preciso de algumas informações suas. Pode me dizer seu nome completo, por favor?\", \"pedido\": {}}\n```\n\nCliente: Kauê Fernandes Braz  \n```json\n{\"resposta\": \"Ótimo, Kauê Fernandes Braz. E qual seria seu email para contato?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\"}}}\n```\n\nCliente: kaue@gmail.com.br  \n```json\n{\"resposta\": \"Tudo certo. Agora, me fale seu número de telefone, por favor.\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\"}}}\n```\n\nCliente: 11932419398  \n```json\n{\"resposta\": \"Perfeito! E qual o seu endereço completo para entrega?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\"}}}\n```\n\nCliente: Rua Isaar Carlos de Carmargo, 395  \n```json\n{\"resposta\": \"Ótimo! Agora, qual celular você deseja comprar?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}}}\n```\n\nCliente: Gostaria de comprar um iPhone, qual tem?  \n```json\n{\"resposta\": \"Temos o iPhone 13, com 128GB de armazenamento e 4GB de RAM, por R$ 5.499,00. Você gostaria de adicionar esse modelo ao seu pedido?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}}}\n```\n\nCliente: Gostaria de adicionar ao pedido  \n```json\n{\"resposta\": \"Perfeito! Quantos iPhones 13 você deseja?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}, \"itens\": [{\"produto\": \"iPhone 13\", \"quantidade\": null, \"preco_unitario\": \"5.499,00\"}]}}\n```\n\nCliente: 1  \n```json\n{\"resposta\": \"Ótimo! E qual a data que você deseja que a entrega seja realizada?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}, \"itens\": [{\"produto\": \"iPhone 13\", \"quantidade\": 1, \"preco_unitario\": \"5.499,00\"}]}}\n```\n\nCliente: Para dia 26 de Outubro de 2024  \n```json\n{\"resposta\": \"Tudo certo! E qual a forma de pagamento que você prefere?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}, \"data_pedido\": \"26 de Outubro de 2024\", \"itens\": [{\"produto\": \"iPhone 13\", \"quantidade\": 1, \"preco_unitario\": \"5.499,00\"}]}}\n```\n\nCliente: Cartão de Crédito  \n```json\n{\"resposta\": \"Ok! Para finalizar, me diga qual o tipo de cartão: Visa, Mastercard, Elo, etc.\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}, \"data_pedido\": \"26 de Outubro de 2024\", \"itens\": [{\"produto\": \"iPhone 13\", \"quantidade\": 1, \"preco_unitario\": \"5.499,00\"}]}}\n```\n\nCliente: Mastercard  \n```json\n{\"resposta\": \"Perfeito! Deseja adicionar algo mais? Caso não, diga exatamente a seguinte frase: 'Finalizar Pedido'.\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}, \"data_pedido\": \"26 de Outubro de 2024\", \"itens\": [{\"produto\": \"iPhone 13\", \"quantidade\": 1, \"preco_unitario\": \"5.499,00\"}], \"forma_pagamento\": {\"tipo\": \"Cartão de Crédito: Mastercard\"}}}\n```\n\nAlguns tratamentos que você deve fazer das respostas caso aconteçam\n\"entrada: lucas arroba gmail.com\\ncorreção: lucas@gmail.com\",\n\"entrada: exemplo ponto com\\ncorreção: exemplo.com\",\n\"entrada: um dois três quatro cinco\\ncorreção: 12345\",\n\"entrada: cinco cinco cinco um dois três quatro cinco\\ncorreção: 555123456\",\n\"entrada: telefone um dois três quatro cinco seis sete oito nove zero\\ncorreção: 1234567890\",\n\"entrada: dois mil e vinte e quatro\\ncorreção: 2024\",\n\"entrada: seis ponto cinco\\ncorreção: 6.5\",\n\"entrada: um vírgula dois\\ncorreção: 1.2\",\n\"entrada: zero vírgula cinco\\ncorreção: 0.5\",\n\"entrada: um mil e novecentos e noventa e nove\\ncorreção: 1999\"\n\nDepois de confirmar que o cliente deseja finalizar o pedido, a confirmação deve ser a última pergunta, onde será falado: você confirma que o pedido está correto? Responda com um 'sim' ou 'não',\nAguarde o retorno do cliente e após o sim, finalize o pedido com a confirmação da conclusão. Caso o cliente não confirme, cancele o pedido, deixe claro que o pedido foi cancelado e não será realizado."
                "Agora segue a conversa atualizada atual com o cliente, ao pegar todas informações diga para ele dizer 'finalizar pedido' caso queira finalizar e antes disso dê um resumo de produtos e valor total da compra, não se esqueça de perguntar se ele quer adicionar algo mais antes, siga o pedido abaixo e responda sempre neste formato (```json\n{ \n\"resposta\": \"uma string com uma resposta de forma natural para o assistente de voz responder\",\n\"pedido\": {\"cliente\": {\"nome\": \"nomeCliente\", \"email\": \"emailCliente\", \"telefone\": \"telefoneCliente\", \"endereco\": \"enderecoCliente\"}, \"data_pedido\": \"dataPedido\", \"itens\": [{ \"produto\": \"Produto1\", \"quantidade\": \"quantidadePedido\", \"preco_unitario\": \"precoProduto\"}, { \"produto\": \"Produto2\", \"quantidade\": \"quantidadePedido\", \"preco_unitario\": \"precoProduto\"}], \"total_pedido\": \"somaPrecoProdutos\", \"forma_pagamento\": {\"tipo\": \"TipoPagamento\"}}\n}\n```)"
            ],
        }
    ]
    for entry in chat_history:
        if "user" in entry:
            history.append({"role": "user", "parts": [entry["user"]]})
        if "model" in entry:
            history.append({"role": "user", "parts": [entry["model"]]})

    print("history", history)

    # Enviar mensagem para o modelo
    chat = model.start_chat(history=history)

    response = chat.send_message(texto)
    resposta = response.text[:1000]
    print("Resposta recebida:", resposta)  # Adicionando impressão da resposta

    # Verificar se a resposta está vazia
    if not resposta.strip():
        print("A resposta recebida está vazia.")
        return None  # ou trate conforme necessário

    # Tentar decodificar o JSON
    try:
        # Limpar as marcações ``json`` da resposta se existirem
        resposta_limpa = resposta.replace("```json", "").replace("```", "").strip()

        # Decodificar a resposta JSON
        data = json.loads(resposta_limpa)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        print(f"Resposta recebida: {resposta}")
        return None  # ou trate o erro de acordo

    # Extrair apenas a resposta desejada
    resposta_limpa = data.get("resposta", "")
    pedido = data.get("pedido", {})
    print("pedido:", pedido)

    return resposta_limpa, pedido


# Função para informar as horas
def informar_horas():
    agora = datetime.now()
    hora = agora.hour
    minuto = agora.minute
    falar(f"Agora são {hora} horas e {minuto} minutos")

def adicionar_pedido_banco(pedido):
    # Função responsável por adicionar o pedido ao banco de dados.
    # Aqui você pode incluir a lógica para inserir o pedido em um banco MongoDB ou qualquer outro.
    # Exemplo básico de inserção no MongoDB:
    try:
        db = conectar_mongo()
        pedidos_collection = db["orderaicollection"]
        pedidos_collection.insert_one(pedido)
        print("Pedido adicionado ao banco de dados com sucesso!")
    except Exception as e:
        print(f"Erro ao adicionar o pedido ao banco de dados: {e}")


# Função principal
def main():
    ativo = False  # Variável para controle do estado
    chat_history = []  # Lista para armazenar o histórico da conversa
    pedido = {}  # Variável para armazenar o pedido
    while True:
        if not ativo:
            command = escutar()
            if "ok fiapinho" in command:
                ativo = True
                falar("Olá. Como posso te ajudar?")

        if ativo:
            command = escutar()
            # Adiciona o comando ao histórico
            chat_history.append({"user": command})

            if "que horas são" in command:
                informar_horas()
            elif "conectar com o banco" in command:
                conectar_mongo()
            elif "finalizar pedido" in command:
                adicionar_pedido_banco(pedido)
                falar("Pedido finalizado")
            elif "sair" in command:
                falar("Até mais!")
                ativo = False
                # Exibe o histórico de chat ao final da conversa
                print("\nHistórico da Conversa:")
                for entry in chat_history:
                    print(f"Usuário: {entry['user']}, Gemini: {entry.get('model', 'Sem resposta')}")
                chat_history = []  # Limpa o histórico ao sair da conversa
            else:
                resposta_gemini, pedido = gerar_resposta(command, chat_history)
                # Adiciona a resposta do Gemini ao histórico
                chat_history[-1]["model"] = resposta_gemini

                print(f"Resposta do Gemini: {resposta_gemini}")
                print(f"PEDIDO ATUALIZADO: {pedido}")
                falar(resposta_gemini)

if __name__ == "__main__":
    main()