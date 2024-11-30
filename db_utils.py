import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os


# Carrega variáveis de ambiente
load_dotenv()

def get_database_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        if connection.is_connected():
            # print("Conectado ao banco de dados MySQL")
            return connection
    except Error as e:
        print(f"Erro ao conectar ao banco de dados MySQL: {e}")
        return None


# Função para inserir dados no banco de dados
def insert_data(connection, query, values):
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()
        print("Dados inseridos com sucesso")
    except Error as e:
        print(f"Erro ao inserir dados no MySQL: {e}")
    finally:
        cursor.close()


# Função para ler dados no banco de dados
def read_data(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Erro ao ler dados no MySQL: {e}")
    finally:
        cursor.close()


# Função para atualizar dados no banco de dados
def update_data(connection, query, values):
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()
        print("Dados atualizados com sucesso")
    except Error as e:
        print(f"Erro ao atualizar dados no MySQL: {e}")
    finally:
        cursor.close()


# Função para deletar dados no banco de dados
def delete_data(connection, query, values):
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        print("Dados deletados com sucesso")
    except Error as e:
        print(f"Erro ao deletar dados no MySQL: {e}")
        raise e
    finally:
        cursor.close()

# Função para criar query de inserção de dados
def create_insert_query(table, columns):
    query = f"INSERT INTO {table} ("
    query += ", ".join(columns)
    query += ") VALUES ("
    query += ", ".join(["%s" for _ in columns])
    query += ")"

    return query


# Função para criar query de leitura de dados
def create_read_query(table, columns=None):
    query = f"SELECT "
    if columns:
        query += ", ".join(columns)
    else:
        query += "*"
    query += f" FROM {table}"

    return query


# Função para criar query de atualização de dados
def create_update_query(table, columns, condition):
    query = f"UPDATE {table} SET "
    query += ", ".join([f"{column} = %s" for column in columns])
    query += f" WHERE {condition}"

    return query


# Função para criar query de deleção de dados
def create_delete_query(table, condition):
    query = f"DELETE FROM {table} WHERE {condition}"

    return query