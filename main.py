import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
from datetime import datetime
#from playsound import playsound
import time
import json
from mongo_connection import conectar_mongo
from flask import Flask, request, jsonify, render_template, send_file, session
from flask_session import Session

app = Flask(__name__)

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

    response = send_file(filename, mimetype="audio/mpeg", as_attachment=False)
    os.remove(filename)

    return response


# Função para ouvir comando de voz
# def escutar():
#     with sr.Microphone() as source:
#         print("Escutando...")
#         audio = recognizer.listen(source)
#         try:
#             command = recognizer.recognize_google(audio, language='pt')
#             print(f"Você disse: {command}")
#             return command.lower()
#         except sr.UnknownValueError:
#             print("Desculpe, não entendi o que você disse.")
#             return ""
#         except sr.RequestError:
#             print("Erro ao conectar com o serviço de reconhecimento de voz.")
#             return ""


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
  upload_to_gemini("Menu-Celulares.csv", mime_type="text/csv"),
  upload_to_gemini("ProdutosAdicionais.csv", mime_type="text/csv")
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
                files[1],
                "Você é um assistente de vendas para produtos de tecnologia, e sua função é registrar pedidos e oferecer sugestões de produtos adicionais conforme as preferências do cliente. Não fale sobre nada além de fazer pedidos de eletrônicos para o cliente, nunca.\n\nSeu objetivo é fazer todo o processo de pedido do cliente, desde pegar as informações pessoais, dados de entrega, até a finalização do pedido.\n\nPara pegar as informações sobre o menu olhe o Menu-Celulares.csv e sobre produtos adicionais recomendados o ProdutosAdicionais.csv, desta forma terá todas as respostas necessárias para o cliente.\n\nDeixe as respostas limpas, de forma que não tenha emojis, nem bullets e outras coisas que uma resposta por voz natural não consiga expressar, também evite de falar 'Olá'. \n\n\nresponda no seguinte formato:\n\n```json\n{ \n\"resposta\": \"uma string com uma resposta de forma natural para o assistente de voz responder\",\n\"pedido\": {\"cliente\": {\"nome\": \"nomeCliente\", \"email\": \"emailCliente\", \"telefone\": \"telefoneCliente\", \"endereco\": \"enderecoCliente\"}, \"prazo_entrega\": \"prazoEntrega\", \"itens\": [{ \"produto\": \"Produto1\", \"quantidade\": \"quantidadePedido\", \"preco_unitario\": \"precoProduto\"}, { \"produto\": \"Produto2\", \"quantidade\": \"quantidadePedido\", \"preco_unitario\": \"precoProduto\"}], \"total_pedido\": \"somaPrecoProdutos\", \"forma_pagamento\": {\"tipo\": \"TipoPagamento\"}}\n}\n```\n\nFaça as perguntas necessárias até que sejam respondidas todos parametros do json do pedido. NUNCA altere as informações já fornecidas pelo cliente, como nome, email, telefone e endereço. Essas informações devem permanecer as mesmas durante todo o processo de pedido.\n\nSe o cliente responder algo que requer confirmação com 'sim' ou 'não', siga o fluxo apropriado, fazendo a próxima pergunta relacionada ao pedido. Caso o cliente queira adicionar itens, sempre pergunte quantos e se deseja continuar com o pedido.\n\nUma vez o cliente respondendo, não altere NUNCA o pedido dele com outra informação, exemplo: trocar de lucas@gmail.com para kaue@gmail.com, somente altere os itens do pedido se o Cliente pedir e caso ele queira cancelar o pedido, apague tudo. Siga estas orientações: 1- Registre todas as informações do pedido 2- Ofertas e recomendações. Sempre que o cliente selecionar um produto, sugira também produtos relacionados considerando: mesma marca e modelo atualizado - se houver uma versão mais nova ou com maior capacidade de armazenamento ou RAM, ofereça essa opção como uma alternativa de upgrade. Especificações Semelhantes: Caso o cliente deseje um modelo específico com características específicas de armazenamento e RAM, ofereça alternativas de outras marcas com especificações similares. Faixa de Preço: Sugira produtos de preço equivalente, ou até 20% superior, ao produto selecionado, oferecendo modelos da mesma marca ou concorrentes.\n\nExemplos - Este é um exemplo de como poder ser o processo, serão diversos clientes\n\nCliente: Quais itens tem no menu?  \n```json\n{\"resposta\": \"No momento, temos os seguintes modelos de celulares disponíveis: Iphone, Motorola, Samsung, Xiaomi e Google. Em qual modelo você está interessado?\", \"pedido\": {}}\n```\n\nCliente: Qual o preço do iPhone 13?  \n```json\n{\"resposta\": \"O iPhone 13 da Apple custa R$ 6.999,00. Como recomendação, você também pode considerar o iPhone 15, que possui mais armazenamento e memória e custa R$ 9.100,00. Gostaria de saber mais sobre ele?\", \"pedido\": {}}\n```\n\nCliente: Sim, gostaria\n ```json\n{\"resposta\": \"O Iphone 15 tem 512 Gigas de armazenamento e 4 Gigas de memória por R$ 9.100,00. Como recomendação, você pode levar uma capinha e película deste modelo e também carregador e AirPods\", \"pedido\": {}}\n```\n\nCliente: Gostaria de fazer um pedido  \n```json\n{\"resposta\": \"Com certeza! Para começar, preciso de algumas informações suas. Pode me dizer seu nome completo, por favor?\", \"pedido\": {}}\n```\n\nCliente: Kauê Fernandes Braz  \n```json\n{\"resposta\": \"Ótimo, Kauê! E qual seria seu email para contato?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\"}}}\n```\n\nCliente: kaue@gmail.com.br  \n```json\n{\"resposta\": \"Tudo certo. Agora, me fale seu número de telefone, por favor.\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\"}}}\n```\n\nCliente: 11932419398  \n```json\n{\"resposta\": \"Perfeito! E qual o seu endereço completo para entrega?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\"}}}\n```\n\nCliente: Rua Isaar Carlos de Carmargo, 395  \n```json\n{\"resposta\": \"Ótimo! Agora, qual celular você deseja comprar?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}}}\n```\n\nCliente: Gostaria de comprar um iPhone, qual tem?  \n```json\n{\"resposta\": \"Temos o iPhone 13, com 128GB de armazenamento e 4GB de RAM, por R$ 3.788,00. Você gostaria de adicionar esse modelo ao seu pedido?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}}}\n```\n\nCliente: Gostaria de adicionar ao pedido  \n```json\n{\"resposta\": \"Perfeito! Recomendo adicionar capinha, película, carregador ou até mesmo Air Pods. Gostaria de algum destes?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}, \"itens\": [{\"produto\": \"iPhone 13\", \"quantidade\": null, \"preco_unitario\": \"3.788,00\"}]}}\n```\n\nCliente: Quero a capinha e o carregador  \n```json\n{\"resposta\": \"Ótimo! O prazo de entrega é de 2 semanas apartir da confirmação do pedido. Qual forma de pagamento você prefere?\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}, \"prazo_entrega\": \"2 semanas\", \"itens\": [{\"produto\": \"iPhone 13\", \"quantidade\": 1, \"preco_unitario\": \"3.788,00\"}, {\"produto\": \"Capinha Iphone 13\", \"quantidade\": 1, \"preco_unitario\": \"30,00\"}, {\"produto\": \"Carregador Iphone\", \"quantidade\": 1, \"preco_unitario\": \"100,00\"} ]}}\n```\n\nCliente: Cartão de Crédito  \n\n```json\n{\"resposta\": \"Perfeito! O seu pedido é 1 Iphone 13 por R$ 3.788,00, uma capinha por R$ 30,00 e um carregador por R$ 100,00, totalizando R$ 3.918,00. Deseja adicionar algo mais? Caso não, diga exatamente a seguinte frase: 'Finalizar Pedido'.\", \"pedido\": {\"cliente\": {\"nome\": \"Kauê Fernandes Braz\", \"email\": \"kaue@gmail.com.br\", \"telefone\": \"11932419398\", \"endereco\": \"Rua Isaar Carlos de Carmargo, 395\"}, \"prazo_entrega\": \"2 semanas\", \"itens\": [{\"produto\": \"iPhone 13\", \"quantidade\": 1, \"preco_unitario\": \"3.788,00\"}, {\"produto\": \"Capinha Iphone 13\", \"quantidade\": 1, \"preco_unitario\": \"30,00\"}, {\"produto\": \"Carregador Iphone\", \"quantidade\": 1, \"preco_unitario\": \"100,00\"}], \"total_pedido\": \"3.918,00\", \"forma_pagamento\": {\"tipo\": \"Cartão de Crédito\"}}}\n```\n\nAlguns tratamentos que você deve fazer das respostas caso aconteçam\n\"entrada: lucas arroba gmail.com\\ncorreção: lucas@gmail.com\",\n\"entrada: exemplo ponto com\\ncorreção: exemplo.com\",\n\"entrada: um dois três quatro cinco\\ncorreção: 12345\",\n\"entrada: cinco cinco cinco um dois três quatro cinco\\ncorreção: 555123456\",\n\"entrada: telefone um dois três quatro cinco seis sete oito nove zero\\ncorreção: 1234567890\",\n\"entrada: dois mil e vinte e quatro\\ncorreção: 2024\",\n\"entrada: seis ponto cinco\\ncorreção: 6.5\",\n\"entrada: um vírgula dois\\ncorreção: 1.2\",\n\"entrada: zero vírgula cinco\\ncorreção: 0.5\",\n\"entrada: um mil e novecentos e noventa e nove\\ncorreção: 1999\"\n\nNão faça respostas longas, sempre tente ser objetivo, por exemplo se for perguntado dos produtos, não fale cada um deles, fale no geral quais marcas que tem por exemplo,\ Caso a resposta seja fora do contexto, diga que não entendeu. Não se esqueça de sempre recomendar os produtos adicionais do ProdutosAdicionais.csv, sempre dê recomendações e análises profundas podendo até fazer comparativos entre modelos"
                "Agora segue a conversa atualizada atual com o cliente, ao pegar todas informações, retorne o resumo do pedido e sempre pergunte para induzir ele a dizer exatamente 'finalizar pedido' caso queira finalizar e antes disso SEMPRE dê um resumo de produtos e valor total da compra, não se esqueça de perguntar se ele quer adicionar algo mais antes, sempre tente ajudar ele a fazer o melhor pedido de forma amigável, agora siga o pedido abaixo e responda sempre neste formato (```json\n{ \n\"resposta\": \"uma string com uma resposta de forma natural para o assistente de voz responder\",\n\"pedido\": {\"cliente\": {\"nome\": \"nomeCliente\", \"email\": \"emailCliente\", \"telefone\": \"telefoneCliente\", \"endereco\": \"enderecoCliente\"}, \"prazo_entrega\": \"prazoEntrega\", \"itens\": [{ \"produto\": \"Produto1\", \"quantidade\": \"quantidadePedido\", \"preco_unitario\": \"precoProduto\"}, { \"produto\": \"Produto2\", \"quantidade\": \"quantidadePedido\", \"preco_unitario\": \"precoProduto\"}], \"total_pedido\": \"somaPrecoProdutos\", \"forma_pagamento\": {\"tipo\": \"TipoPagamento\"}}\n}\n```)"
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

# Rota para exibir a página HTML com o botão
@app.route("/")
def index():
    return render_template("index.html")  # Renderiza o arquivo HTML

# Configuração da sessão
app.config['SESSION_TYPE'] = 'filesystem'  # Armazenamento em sistema de arquivos
app.secret_key = 'your_secret_key'  # Chave secreta para proteger as sessões
Session(app)  # Inicializa a extensão de sessão

@app.route("/iniciar_fala", methods=["POST"])
def main():
    data = request.json  # Obtém os dados JSON do POST
    command = data.get("command", "")  # Obtém o comando reconhecido
    chat_history = session.get('chat_history', [])  # Obtém o histórico de chat da sessão
    pedido = {}  # Variável para armazenar o pedido

    # Adiciona o comando ao histórico
    chat_history.append({"user": command})

    if "que horas são" in command:
        resposta = informar_horas()  # Supondo que essa função retorne uma resposta
        return jsonify({"message": "Comando processado", "resposta": resposta}), 200
    elif "finalizar pedido" in command:
        adicionar_pedido_banco(pedido)
        resposta = "Pedido finalizado"  # Retorna a resposta como string
        # Adiciona a resposta do Gemini ao histórico
        chat_history.append({"model": resposta})
        session['chat_history'] = []  # Limpa o histórico da sessão
        return jsonify({"message": "Comando processado", "resposta": resposta}), 200  # Responde com a mensagem
    elif "sair" in command:
        resposta = "Até mais!"  # Resposta ao sair
        # Exibe o histórico de chat ao final da conversa
        print("\nHistórico da Conversa:")
        for entry in chat_history:
            print(f"Usuário: {entry['user']}, Gemini: {entry.get('model', 'Sem resposta')}")
        session['chat_history'] = []  # Limpa o histórico ao sair da conversa
        return jsonify({"message": "Conversa encerrada", "resposta": resposta}), 200  # Finaliza a conversa
    else:
        resposta_gemini, pedido = gerar_resposta(command, chat_history)
        # Adiciona a resposta do Gemini ao histórico
        chat_history[-1]["model"] = resposta_gemini

        print(f"Resposta do Gemini: {resposta_gemini}")
        print(f"PEDIDO ATUALIZADO: {pedido}")

        session['chat_history'] = chat_history  # Atualiza o histórico na sessão

        return jsonify({"message": "Comando processado", "resposta": resposta_gemini}), 200  # Responde com a mensagem




if __name__ == "__main__":
    app.run(debug=True)