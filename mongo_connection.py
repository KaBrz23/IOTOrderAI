from pymongo import MongoClient

def conectar_mongo():
    try:
        # Conectando ao MongoDB com URI completa
        client = MongoClient(
            "mongodb+srv://rm97768:Kaue2005_@orderai-mongodb.mongocluster.cosmos.azure.com/?authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000&appName=mongosh+1.10.1")

        # Testando a conexão
        client.admin.command('ping')
        print("Conexão bem-sucedida ao MongoDB!")

        # Especificando o banco de dados
        db = client['orderai']  # Substitua 'nome_do_banco' pelo nome correto do seu banco de dados

        return db  # Retorna o banco de dados diretamente para futuras operações

    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return None