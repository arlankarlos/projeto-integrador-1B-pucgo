from db_utils import create_insert_query, insert_data, create_read_query, read_data
from validate_utils import validate_email, validate_phone, validate_cep, validate_uf
import datetime


# Função ler dados para criar novo usuário
def read_user_data():
    nome = input("Nome: ")
    while not validate_email(email := input("Email: ")):
        print("Email inválido - tente novamente\n exemplo@email.com")
    while not validate_phone(telefone := input("Telefone: ").replace("(", "").replace(")", "").replace("-", "").replace(" ", "")):
        print("Telefone inválido - tente novamente\n (11) 91234-5678")
    data_cadastro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (nome, email, telefone, data_cadastro)


# Função para ler o endereço completo de um usuário
def read_user_full_address():
    logradouro = input("Logradouro: ")
    numero = input("Número: ")
    if not numero or not numero.isdigit():
        numero = None
    complemento = input("Complemento: ")
    bairro = input("Bairro: ")
    while not validate_cep(cep := input("CEP: ").replace("-", "").replace(".", "").replace(" ", "")):
        print("CEP inválido - tente novamente\n 12345-678")
    cidade = input("Cidade: ")
    while not validate_uf(estado := input("Estado (UF): ")):
        print("Estado inválido - tente novamente\n SP or GO or RS")
    return (logradouro, numero, complemento, bairro, cep, cidade, estado)


# Função ler usuario_id da tabela usuarios e endereço_id da tabela endereco
def get_usuario_id_endereco_id(connection):

    query = create_read_query("usuarios", ["usuario_id"])
    result = read_data(connection, query)
    result.sort()
    usuario_id = result[-1][0]
    query = create_read_query("endereco", ["endereco_id"])
    result = read_data(connection, query)
    result.sort()
    endereco_id = result[-1][0]
    return (usuario_id, endereco_id)


# Função tabela de relacionamento usuarioendereco
def create_user_address(connection):
    query = create_insert_query(
        "usuarioendereco", ["usuario_id", "endereco_id"]
    )
    values = get_usuario_id_endereco_id(connection)
    insert_data(connection, query, values)



# Função para criar novo usuário
def create_user(connection):
    query = create_insert_query(
        "usuarios", ["nome", "email", "telefone", "data_cadastro"]
    )
    values = read_user_data()
    insert_data(connection, query, values)

    query = create_insert_query(
        "endereco", ["logradouro", "numero", "complemento", "bairro", "cep", "cidade", "estado"]
    )
    values = read_user_full_address()
    insert_data(connection, query, values)
    create_user_address(connection)