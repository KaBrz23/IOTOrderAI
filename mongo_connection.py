from pymongo import MongoClient

def conectar_mongo():
    try:
        # Conectando ao MongoDB com URI completa
        client = MongoClient(
            "mongodb+srv://rm97768:Kaue2005_@orderai-mongodb.mongocluster.cosmos.azure.com/?authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000&appName=mongosh+1.10.1")

        # Testando a conexão
        client.admin.command('ping')
        print("Conexão bem-sucedida ao MongoDB!")

        return client  # Retorna o cliente para futuras operações no banco

    except ConnectionError as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return None