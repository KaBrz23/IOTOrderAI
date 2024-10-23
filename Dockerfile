FROM python:3-alpine3.15

WORKDIR /app

# Copia os arquivos da aplicação, exceto os que estão no .dockerignore
COPY . /app

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que a aplicação Flask utiliza
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["python", "./main.py"]
